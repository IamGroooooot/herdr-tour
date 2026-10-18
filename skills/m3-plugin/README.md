# m3-plugin

개념도: [diagram.html](diagram.html)

**plugin은 '언제'(trigger)를 적은 manifest(`herdr-plugin.toml`)와 '무엇을'(명령)의 묶음이다. 명령은 `"$HERDR_BIN_PATH"`로 herdr CLI를 부른다. SDK는 없고 CLI 전체가 plugin API다.**

## trigger

| entrypoint | 언제 |
| --- | --- |
| `[[actions]]` | 직접 실행(CLI, key) |
| `[[events]]` | event가 날 때 |
| `[[panes]]` | plugin 화면을 열 때 |
| `[[link_handlers]]` | 링크를 Ctrl-click할 때 |
| `[[startup]]` | server가 켜질 때. link나 reload로는 돌지 않는다 |

## 예시

| 예시 | trigger | 하는 일 | 보이는 곳 |
| --- | --- | --- | --- |
| 팀 보드 | `[[actions]]`, `[[panes]]` popup | agent 목록을 state 순으로 2초마다 다시 그린다 | popup |
| swarm 버튼 | `[[actions]]` | `m2-swarm`의 worktree와 agent 셋을 한 번에 | 새 workspace 셋 |
| worktree 자동 투입 | `[[events]]` `worktree.created` | 새 worktree의 root pane에 claude를 띄운다 | sidebar |
| reviewer 소환 | `[[actions]]` | focus된 pane 옆에 reviewer를 띄워 `git diff`를 리뷰시킨다 | split pane |
| 링크를 pm에게 | `[[link_handlers]]` | GitHub issue 링크 Ctrl-click을 pm에게 일로 보낸다 | pm pane |
| 끝 시각 요약 | `[[events]]` `pane.agent_status_changed` | done이면 걸린 시간을 sidebar `$summary`로 | sidebar(`p2-events`) |

엮는 법

- swarm 버튼 + worktree 자동 투입: 버튼은 worktree만 만들고, agent는 자동 투입이 붙인다.
- 링크를 pm에게 + swarm 버튼: issue 링크를 누르면 pm이 worktree를 나눠 맡긴다.
- reviewer 소환 + 끝 시각 요약: 리뷰가 끝나면 sidebar에 걸린 시간이 남는다.

## 명령

1. `mkdir -p ~/herdr-plugins/<id>` -> 아래 "시작 코드"에서 출발해 manifest와 `plugin.sh`를 쓴다.
2. `herdr plugin link ~/herdr-plugins/<id>`: manifest를 고칠 때마다 다시 한다. `plugin.sh` 수정은 바로 반영된다.
3. trigger 일으키기
   - action: `herdr plugin action invoke <id>.<action>`. CLI로 부르면 사람이 지금 보고 있는 workspace와 pane이 context다. swarm 버튼은 sidebar에서 `demo`를 연 상태로 부른다.
   - pane: `herdr plugin pane open --plugin <id> --entrypoint <pane>`
   - event: 그 일을 직접 한다(예: `herdr worktree create`).
   - 링크: pane에 URL을 찍고 Ctrl-click
4. 확인: `herdr plugin list`, `herdr plugin action list --plugin <id>`, `herdr plugin log list --plugin <id>`
5. 키에 묶기(설정 파일 백업 뒤, `p2-events` 참고): `[[keys.command]]`에 `key = "prefix+B"`, `type = "plugin_action"`, `command = "<id>.board"`

## 시작 코드

`~/herdr-plugins/me.team/herdr-plugin.toml`

```toml
id = "me.team"
name = "Team"
version = "0.1.0"
min_herdr_version = "0.9.0"
platforms = ["linux", "macos"]

[[actions]]
id = "board"
title = "Team board"
contexts = ["workspace"]
command = ["bash", "plugin.sh", "open-board"]

[[panes]]
id = "board"
title = "Team board"
placement = "popup"
width = "70%"
height = "60%"
command = ["bash", "plugin.sh", "board"]
```

`~/herdr-plugins/me.team/plugin.sh`. 기능 하나 = manifest entrypoint 하나 + `main`의 case 한 줄 + 함수 하나

```bash
#!/usr/bin/env bash
set -eu

main() {
  case "${1:-}" in
    open-board) h plugin pane open --plugin "$HERDR_PLUGIN_ID" --entrypoint board ;;
    board) board ;;
    *) echo "unknown entry: ${1:-}" >&2; exit 2 ;;
  esac
}

board() {
  while :; do
    clear
    h agent list | jq -r '.result.agents[] | "\(.agent_status)\t\(.name // .agent)\t\(.tokens.summary // "")"' | sort
    read -r -s -t 2 -n 1 key && [ "$key" = q ] && exit 0
  done
}

h() { "$HERDR_BIN_PATH" "$@"; }
ctx() { printf '%s' "${HERDR_PLUGIN_CONTEXT_JSON:-}" | jq -r "$1 // empty"; }
evt() { printf '%s' "${HERDR_PLUGIN_EVENT_JSON:-}" | jq -r "$1 // empty"; }

main "$@"
```

다른 예시의 함수. 맨 아래 `main "$@"`보다 위에 넣고, `main`의 case에 한 줄을 더한다.

```bash
swarm() {        # [[actions]] id = "swarm"
  for i in a b c; do
    r=$(h worktree create --cwd "$(ctx .workspace_cwd)" --branch "swarm/$i" --label "$i" --no-focus | jq -r '.result.root_pane.pane_id')
    h agent start "s-$i" --kind claude --pane "$r" -- --permission-mode acceptEdits || true
  done
}

on_worktree() {  # [[events]] on = "worktree.created"
  p=$(h pane list --workspace "$(evt .data.workspace.workspace_id)" | jq -r '.result.panes[0].pane_id')
  h agent start "wt-$(date +%s)-$$" --kind claude --pane "$p" -- --permission-mode acceptEdits || true
}

review() {       # [[actions]] id = "review"
  n="rv-$(date +%s)-$$"
  r=$(h pane split "$(ctx .focused_pane_id)" --direction right --no-focus | jq -r '.result.pane.pane_id')
  h agent start "$n" --kind claude --pane "$r" && h agent prompt "$n" "지금 git diff를 리뷰해 줘. 다섯 줄 이내로."
}

to_pm() {        # [[actions]] id = "to-pm" + [[link_handlers]] id, title, pattern = "^https://github\\.com/[^/]+/[^/]+/issues/[0-9]+$", action = "to-pm"
  h agent prompt pm "이 이슈를 front, back과 처리해 줘: $(ctx .clicked_url)"
}
```

## 참고

- 관리: `herdr plugin disable <id>`, `herdr plugin enable <id>`, `herdr plugin config-dir <id>`(`.env` 같은 사용자 설정), `herdr plugin unlink <id>`
- plugin pane: `herdr plugin pane focus <pane>`, `herdr plugin pane close <pane>`
- 배포: GitHub repo에 topic `herdr-plugin`을 붙이면 marketplace에 실린다. 받는 쪽은 `herdr plugin install owner/repo[/subdir]`, `herdr plugin update`, `herdr plugin uninstall <id>`
- 환경 변수: `HERDR_BIN_PATH`, `HERDR_PLUGIN_ID`, `HERDR_PLUGIN_STATE_DIR`(기억할 파일), `HERDR_PLUGIN_CONTEXT_JSON`(workspace, focus된 pane, 클릭한 URL), `HERDR_PLUGIN_EVENT_JSON`(event와 `.data`)
