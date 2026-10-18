# b2-team

개념도: [diagram.html](diagram.html)

**화면은 workspace > tab > pane 세 층이고, agent는 pane 안에서 돈다. CLI로 만들면 새 ID는 응답으로 오고, 사람의 focus는 그대로다.**

## 명령

준비

1. `mkdir -p ~/herdr-demo && git -C ~/herdr-demo init -q -b main`
2. `herdr workspace create --cwd ~/herdr-demo --label demo --no-focus`
   - `.result.workspace.workspace_id`가 `<ws>`, `.result.tab.tab_id`가 `<t1>`, `.result.root_pane.pane_id`가 `<a>`

`인사` 탭

3. `herdr tab rename <t1> 인사` -> `herdr pane split <a> --direction right --no-focus` -> `<b>`
4. agent 둘을 띄운다.
   - `herdr agent start hi-claude --kind claude --pane <a> -- --allowedTools "Bash(herdr *)"`
   - `herdr agent start hi-codex --kind codex --pane <b>`
5. 아래 문구를 Write 도구로 `/tmp/tour-hi.txt`에 쓰고(따옴표와 backtick이 섞여 있다) `herdr agent prompt hi-claude "$(cat /tmp/tour-hi.txt)" --wait --timeout 120000`
   > 옆 pane의 codex(herdr agent 이름 hi-codex)에게 인사해 줘. `herdr agent prompt hi-codex "<네 인사 한 줄>" --wait --timeout 60000`으로 보내고, `herdr agent read hi-codex --source recent-unwrapped --lines 15`로 답을 읽은 뒤, 그 답에 한 줄로 화답해.

`개발` 탭

6. `herdr tab create --workspace <ws> --label 개발 --no-focus` -> `.result.root_pane.pane_id`가 `<pm>`
7. `herdr pane split <pm> --direction right --ratio 0.6 --no-focus` -> `<front>`, `herdr pane split <front> --direction down --no-focus` -> `<back>`
   - `--ratio`는 원래 pane의 몫이다. 0.6이면 pm이 폭의 60%다.
8. `herdr pane rename <pm> pm`, front와 back도 같은 식으로
9. agent 셋을 동시에 띄운다. 신뢰는 hi-claude에서 한 번 수락하면 같은 폴더에 남는다.
   - `herdr agent start <이름> --kind claude --pane <pane> -- --permission-mode acceptEdits`(pm, front, back)
   - 클로드 세션 이름: 셋마다 `herdr agent prompt <이름> "/rename <이름>"`(`--wait` 없이). SendMessage는 이 세션 이름으로 서로를 찾는다.
10. pm에게 먼저, 그다음 front와 back에게 동시에 역할을 보낸다: `herdr agent prompt <이름> "<문구>" --wait --timeout 120000`
   - pm: "너는 pm이야. ~/herdr-demo에서 front, back 두 agent와 일해. 둘에게는 SendMessage로 @front, @back에게 말하면 돼. 지금은 네 역할을 한 줄로 말해. front와 back이 '준비됨'을 보내오면 받았다고 한 줄로 답해."
   - front: "너는 front 담당이야. 화면을 맡아. 지시는 pm이 SendMessage로 보낼 거야. 지금은 SendMessage로 @pm에게 'front 준비됨'만 보내."
   - back: "너는 back 담당이야. server와 데이터를 맡아. 지시는 pm이 SendMessage로 보낼 거야. 지금은 SendMessage로 @pm에게 'back 준비됨'만 보내."
11. `herdr agent read pm --source recent-unwrapped --lines 20`으로 두 보고가 왔는지 본다.

## 신뢰 질문

새 폴더에서는 `agent start`가 `agent_not_ready`를 돌려준다. `herdr agent read <이름> --source visible`로 커서 위치를 보고 바로 수락한다.

- Claude Code는 커서(`❯`)가 'No, exit'에 있다. `herdr agent send-keys <이름> down enter`로 'Yes, I trust this folder'를 고른다.
- Codex는 화면의 커서 위치를 보고 같은 식으로 고른다.
- 그다음 `herdr agent wait <이름> --until idle --timeout 30000`

## 참고

- workspace: `herdr workspace list/get/focus/rename/close`
- tab: `herdr tab list/get/focus/close`
- pane: `herdr pane list --workspace <ws>`, `herdr pane layout --pane <pm>`(split 트리와 ratio), `herdr pane get`, `herdr pane current`, `herdr pane process-info`, `herdr pane focus --direction left`, `herdr pane neighbor/edges`, `herdr pane resize --direction right --amount 0.1`, `herdr pane zoom`, `herdr pane swap`
- 우클릭을 pane 안 프로그램에 넘기기: `herdr pane input --current --right-click pane`
- tab 구조를 한 번에 만들기: socket method `layout.apply`(`herdr api schema`)
- agent 이름 바꾸기: `herdr agent rename <pane> <이름>`
