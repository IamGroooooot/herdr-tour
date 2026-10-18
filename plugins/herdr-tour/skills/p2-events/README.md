# p2-events

개념도: [diagram.html](diagram.html)

**event는 '바뀌었다'는 신호일 뿐이고, 값은 지금 상태(snapshot)를 다시 읽어 얻는다. 사람에게는 보지 않는 곳의 agent가 끝나거나(`done`) 기다릴 때(`blocked`)만 toast를 보내고, 나머지는 sidebar 한 줄 요약으로 둔다.**

## 알리는 길

| 길 | 언제 | 명령 |
| --- | --- | --- |
| toast | 보지 않는 곳의 agent가 `done`이나 `blocked`일 때 사람을 부른다 | 1~4 |
| sidebar `$summary` | 부를 정도는 아닌 정보를 agent 행 아래 한 줄로 남긴다 | 2, 7 |
| socket 구독 | 프로그램이 여러 pane의 변화를 받는다. 브라우저로 넓히기는 `p3-socket` | 5~6 |
| plugin `[[events]]` hook | event마다 정해 둔 일을 한다 | 7 |

## 명령

1. 백업: 경로는 `herdr --help`의 `Config:` 줄이다. `cp -n <config> <config>.tour-bak`
2. 추가한다. 같은 table이 이미 있으면 그 안에 key만 넣는다(TOML은 table 중복 금지).

   ```toml
   [ui.toast]
   delivery = "herdr"

   [ui.sidebar.agents]
   rows = [["state_icon", "agent", "state_text"], ["$summary"], ["workspace", "tab"]]
   ```

3. `herdr config check` -> `herdr server reload-config`: `applied`. parse error면 `failed`이고 기존 설정이 남는다.
4. toast 확인: `herdr notification show tour --body "toast on" --sound done`의 `shown`이 `true`
5. 구독: `herdr agent get pm`(front, back도)의 pane ID로 `/tmp/tour-sub.json`을 쓴다.

   ```json
   {"id":"sub","method":"events.subscribe","params":{"subscriptions":[{"type":"pane.agent_status_changed","pane_id":"<pm pane>"},{"type":"pane.agent_status_changed","pane_id":"<front pane>"},{"type":"pane.agent_status_changed","pane_id":"<back pane>"}]}}
   ```

   새 pane `<ev>`: `herdr pane run <ev> 'cat /tmp/tour-sub.json - | nc -U "$HERDR_SOCKET_PATH"'`
6. event가 오면 값은 다시 읽는다: `herdr agent get pm`. 전체는 `herdr api snapshot`
7. 끝 시각 요약 hook: manifest에 아래 entrypoint를 더하고, `plugin.sh`의 `main`에 `on-status) on_status ;;`를, 맨 아래 `main "$@"`보다 위에 함수를 넣은 뒤 `herdr plugin link <dir>`

   ```toml
   [[events]]
   on = "pane.agent_status_changed"
   command = ["bash", "plugin.sh", "on-status"]
   ```

   ```bash
   on_status() {
     p=$(evt .data.pane_id)
     f="$HERDR_PLUGIN_STATE_DIR/$(printf '%s' "$p" | tr ':' '_').start"
     case "$(evt .data.agent_status)" in
       working) [ -f "$f" ] || date +%s > "$f" ;;
       done|idle)
         [ -f "$f" ] || return 0
         took=$(( $(date +%s) - $(cat "$f") )); rm -f "$f"
         h pane report-metadata "$p" --source plugin:summary --token summary="$(date +%H:%M) 끝, ${took}초"
         ;;
     esac
   }
   ```

8. 사용자가 다른 workspace로 간 뒤 `herdr agent prompt pm "README.md에 실행법을 세 줄로 써 줘"`(`--wait` 없이). 끝나면 toast가 오고, sidebar의 pm 아래에 `14:03 끝, 52초` 같은 줄이 생긴다.
