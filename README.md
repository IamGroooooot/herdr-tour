# herdr-tour

[herdr](https://herdr.dev) 0.9.5를 몸으로 익히는 agent skill 투어. 데모 팀 하나를 띄우고(초급 6분), 그 팀에 일을 나눠 맡기고(중급 15분), agent team을 간단하게 짜 본 뒤 나만의 Workflow를 만든다(고급).

| 파트 | 시간 | 할 수 있게 되는 일 |
| --- | --- | --- |
| 초급 | 6분 | 여러 agent를 띄워보기 |
| 중급 | 15분 | agent 팀에 일을 나눠 맡기기 |
| 고급 | 자기 속도 | 나만의 Workflow 만들기 |

장면마다 파일이 셋이다.

- `SKILL.md`: 실제 프롬프트처럼 짧은 구어체 요청. herdr pane 안의 agent가 읽고 바로 한다.
- `README.md`: 개념 한 줄과 정확한 명령
- `diagram.html`: 개념도. 전체는 [`index.html`](index.html)에서 한눈에 본다(브라우저로 연다).

개념도와 README는 사이트로도 본다: [iamgroooooot.github.io/herdr-tour](https://iamgroooooot.github.io/herdr-tour/). main에 push하면 `.github/workflows/pages.yml`이 `scripts/build_site.py`로 다시 만든다.

운영 주제(설치, update, channel, troubleshooting, Windows)는 다루지 않는다.

## 준비물

herdr 0.9.5 이상, Claude Code, Codex CLI, git, jq, python3. 미리 깔아 둘 plugin이나 원격 host는 필요 없다.

## herdr 설치

공식 문서: [herdr.dev/docs](https://herdr.dev/docs/) ([Install](https://herdr.dev/docs/install/), [Quick start](https://herdr.dev/docs/quick-start/))

- macOS, Linux: `curl -fsSL https://herdr.dev/install.sh | sh`

설치 후 `herdr --version`으로 확인하고, `herdr`로 실행한다.

## 실행

agent를 herdr pane 안에서 실행한다(`HERDR_ENV=1`). 투어를 진행하는 Claude Code는 herdr, git, mkdir 명령을 미리 허용해 두면 승인 창이 줄어 시간 안에 끝난다: `--allowedTools "Bash(herdr *),Bash(git *),Bash(mkdir *)"`

- Claude Code plugin: `claude plugin marketplace add IamGroooooot/herdr-tour` 후 `claude plugin install herdr-tour@herdr-tour`, 이어서 `/herdr-tour:b1-server`
- Codex plugin: `codex plugin marketplace add IamGroooooot/herdr-tour` 후 `codex plugin add herdr-tour@herdr-tour`, 이어서 `$herdr-tour:b1-server`. Codex용 사본은 [`plugins/herdr-tour`](plugins/herdr-tour)에 있고, AskUserQuestion 대신 `request_user_input`을 쓴다.
- 다른 agent: `npx skills add IamGroooooot/herdr-tour -g`

## 초급 6분: 여러 agent를 띄워보기

| 장면 | 시간 | 하는 일 | 참고 | 개념도 |
| --- | --- | --- | --- | --- |
| [`b1-server`](skills/b1-server/SKILL.md) | 1분 | 터미널 창을 닫아도 pane과 agent는 계속 돈다 | [README](skills/b1-server/README.md) | [diagram](skills/b1-server/diagram.html) |
| [`b2-team`](skills/b2-team/SKILL.md) | 3분 | `인사` 탭(claude와 codex가 인사)과 `개발` 탭(pm, front, back)을 차린다 | [README](skills/b2-team/README.md) | [diagram](skills/b2-team/diagram.html) |
| [`b3-gotopicker`](skills/b3-gotopicker/SKILL.md) | 2분 | pm이 나를 부트스트래핑할 도구를 질문하며 기다리면, Goto picker(`prefix+g`)로 찾아가 답한다 | [README](skills/b3-gotopicker/README.md) | [diagram](skills/b3-gotopicker/diagram.html) |

## 중급 15분: agent 팀에 일을 나눠 맡기기

| 장면 | 시간 | 하는 일 | 참고 | 개념도 |
| --- | --- | --- | --- | --- |
| [`m1-pm`](skills/m1-pm/SKILL.md) | 6분 | pm이 front와 back에게 나눠 맡겨 PLAN.md의 도구를 완성한다 | [README](skills/m1-pm/README.md) | [diagram](skills/m1-pm/diagram.html) |
| [`m2-swarm`](skills/m2-swarm/SKILL.md) | 5분 | worktree 여러 개로 동시에 고치고, 완료 조건으로 확인해 고르거나 합친다(Best-of-N, Divide and Merge, Nominal Group) | [README](skills/m2-swarm/README.md) | [diagram](skills/m2-swarm/diagram.html) |
| [`m3-plugin`](skills/m3-plugin/SKILL.md) | 4분 | 팀에 반응하는 plugin을 그 자리에서 만든다(팀 보드, swarm 버튼, worktree 자동 투입 등) | [README](skills/m3-plugin/README.md) | [diagram](skills/m3-plugin/diagram.html) |

## 고급: 나만의 Workflow 만들기

| 장면 | 시간 | 하는 일 | 참고 | 개념도 |
| --- | --- | --- | --- | --- |
| [`p1-compose`](skills/p1-compose/SKILL.md) | 판마다 8분 | 세 결정(Decomposition, Communication, Convergence)을 내려 그때그때 다른 agent team을 만들어서 herdr로 돌린다 | [README](skills/p1-compose/README.md) | [diagram](skills/p1-compose/diagram.html) |
| [`p2-events`](skills/p2-events/SKILL.md) | 자기 속도 | toast, sidebar 요약, event 구독, plugin hook으로 끝나거나 막힐 때만 알게 한다 | [README](skills/p2-events/README.md) | [diagram](skills/p2-events/diagram.html) |
| [`p3-socket`](skills/p3-socket/SKILL.md) | 자기 속도 | socket 연결을 열어 둔 채 pane 상태를 브라우저에 실시간으로 띄우고, 거기서 입력을 보낸다 | [README](skills/p3-socket/README.md) | [diagram](skills/p3-socket/diagram.html) |
| [`p4-session`](skills/p4-session/SKILL.md) | 자기 속도 | server를 껐다 켜도 일이 이어지게 하고, 원격 machine으로 넓히는 길을 본다 | [README](skills/p4-session/README.md) | [diagram](skills/p4-session/diagram.html) |
