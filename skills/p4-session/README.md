# p4-session

개념도: [diagram.html](diagram.html)

**session은 이름을 붙여 따로 띄운 server다. 다시 켜면 배치(layout)는 돌아오고 돌던 process는 사라진다. resume 정보가 있는 pane만 agent가 다시 시작된다.**

## 되살리는 방식

| 방식 | pane process |
| --- | --- |
| layout 복원(restart) | 저장된 디렉터리의 새 shell |
| resume(`report-agent ... -- <명령>`, `report-agent-session`, integration의 native session 참조) | 새로 시작하되 agent 대화를 다시 연다 |
| live handoff(`herdr update --handoff`, 실험) | 계속 실행 |

- layout은 workspace, tab, pane, cwd를 담은 `session.json`이다.
- resume 정보는 보고된 resume 명령(`report-agent ... -- <명령>`)이나 integration의 session 참조(`report-agent-session`)다.
- named session은 socket, `session.json`, ID를 따로 갖는 별도 server다. config 파일과 plugin은 함께 쓰고, CPU나 filesystem은 격리하지 않는다.

## 명령

main server는 건드리지 않고 sandbox session에서 한다.

1. 새 pane `<sp>`: `herdr pane split --current --direction down --no-focus` -> `herdr pane run <sp> 'herdr --session tour-s server'`
2. `herdr session list`
3. `herdr --session tour-s workspace create --cwd /tmp --label sandbox` -> root `<r>`, `herdr --session tour-s pane split <r> --direction right --no-focus` -> `<v>`
4. 보통 pane: `herdr --session tour-s pane run <v> vim`
5. resume 명령을 보고한 pane(`--` 뒤가 resume 명령)
   - `herdr --session tour-s pane run <r> '"$HERDR_BIN_PATH" pane report-agent "$HERDR_PANE_ID" --source custom:tour --agent tour-bot --state idle --seq "$(date +%s)" --agent-session-id demo -- top; sleep 3600'`
6. `herdr session stop tour-s` -> 1의 `pane run`으로 다시 띄운다.
7. `herdr --session tour-s pane list`로 ID를 다시 읽고 `herdr --session tour-s pane process-info --pane <r>`: `sleep` 대신 `top`이 돈다. `<v>`는 vim 대신 새 shell이다.
8. 사용자: herdr 밖의 새 터미널 창에서 `herdr session attach tour-s`로 직접 본다(`prefix+q`로 나온다). herdr pane 안에서 치면 중첩 실행이 막혀 있어 실패한다.
9. 정리: `herdr session stop tour-s && herdr session delete tour-s`, `herdr pane close <sp>`

## 원격

| 경로 | UI가 도는 곳 | 한 화면에 보이는 server |
| --- | --- | --- |
| SSH로 들어가 원격에서 `herdr` | 원격 | 원격 하나 |
| `herdr --remote <host>` | 내 컴퓨터 | 원격 하나(`--session`, `--remote-keybindings server`) |
| `herdr machine add <host>` | 내 컴퓨터 | Local과 등록한 원격 여럿 |

- `herdr machine add <host> --label <이름>`: 처음 연결할 때 원격에 herdr를 설치하거나 server를 교체할지 묻는다. 기본 답은 No이고, 교체를 고르면 그 server의 pane process는 끝난다.
- `herdr machine list`, `herdr machine status <이름>`, `herdr machine reconnect <이름>`(SSH 재인증), `herdr machine rename <profile-id> --label <새 이름>`, `herdr machine disable <profile-id>`, `herdr machine enable <profile-id>`, `herdr machine remove <profile-id>`(profile만 지우고 원격 session은 남는다)
- `herdr --machine <이름> agent list`: ID와 agent 이름은 server마다 따로라서 원격 대상에는 `--machine`을 붙인다. 화면에서 machine을 골라도 CLI 대상은 바뀌지 않는다.
- 설정 중 보이는 방식은 내 config를, 실행 방식은 그 machine의 config를 따른다.
