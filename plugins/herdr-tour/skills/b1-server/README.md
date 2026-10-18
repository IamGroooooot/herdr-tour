# b1-server

개념도: [diagram.html](diagram.html)

**server 하나가 모든 pane의 프로그램을 쥐고, 터미널 창의 herdr 화면(TUI)은 거기 붙는 client다. 그래서 창을 닫아도 pane과 agent는 계속 돈다.**

## 명령

1. `herdr pane split --current --direction right --no-focus` -> `.result.pane.pane_id`가 `<clock>`
2. `herdr pane run <clock> 'i=0; while :; do i=$((i+1)); echo "$i $(date +%T)"; sleep 1; done'`
3. 사용자: 터미널 창을 닫고(또는 `prefix+q`), 새 터미널에서 `herdr`
4. `herdr pane read <clock> --source recent --lines 120`: 번호가 빠짐없이 이어진다. 시각은 가끔 1초씩 건너뛰니 번호로 본다.
5. `herdr pane close <clock>`

## 참고

- `herdr status`: server와 client 상태. `herdr server`: 화면 없이 server만. `herdr server stop`: server와 모든 pane 종료
- `herdr terminal attach <terminal_id>`(`herdr pane get`의 `terminal_id`): pane 하나에만 붙는 client
- `herdr terminal session observe <pane>`(읽기), `herdr terminal session control <pane>`(읽기와 쓰기): 프로그램용 client
