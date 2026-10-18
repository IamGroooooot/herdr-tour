# p3-socket

개념도: [diagram.html](diagram.html)

**CLI는 요청 하나에 응답 하나를 받고 연결을 닫는다. socket에 `events.subscribe`를 보내면 연결을 열어 둔 채 여러 pane의 변화가 계속 온다. 처음 상태는 `session.snapshot`으로 한 번 받고, 그다음은 event만 반영한다.**

## method

| method | 연결 | `live.py`에서 |
| --- | --- | --- |
| `session.snapshot` | 응답 하나 | 처음, 그리고 pane이 생기거나 닫힐 때 |
| `events.subscribe` | 열어 둔 채 계속 | pane마다 `pane.agent_status_changed`, 그리고 `pane.created`, `pane.closed` |
| `agent.prompt` | 응답 하나 | agent pane에 입력 |
| `pane.send_text` | 응답 하나 | shell pane에 입력(끝에 `\r`) |

[`live.py`](live.py)는 python3 표준 라이브러리만 쓴다. herdr socket과 브라우저 사이에서 event를 SSE로 넘기고, 입력을 method 호출로 바꾼다.

## 명령

1. 새 pane `<live>`: `herdr pane run <live> "python3 <skill 폴더>/live.py"` -> 브라우저로 `http://127.0.0.1:8765`
2. 새 pane `<cli>`: `herdr pane run <cli> "herdr agent wait pm --until working"`
3. 사용자: 브라우저 표에서 pm 행을 고르고 프롬프트를 보낸다. 표는 working, idle로 계속 바뀌고, `<cli>`는 working 한 번에 끝난다.
4. 정리: `herdr pane close <live>`, `herdr pane close <cli>`

## 참고

- 손으로 한 번: `echo '{"id":"s","method":"session.snapshot","params":{}}' | nc -U "$HERDR_SOCKET_PATH"`
- 연결 하나에 요청 하나. 구독한 연결은 event만 받으므로 입력은 새 연결로 보낸다.
- `pane.agent_status_changed`는 `pane_id`가 있어야 구독된다. 새 pane은 `pane.created`를 보고 다시 구독한다.
- 이름 칸은 pane label이다(`b2-team`의 `herdr pane rename`).
- method, event, subscription 목록: `herdr api schema --json`
