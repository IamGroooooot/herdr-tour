# b3-gotopicker

개념도: [diagram.html](diagram.html)

**agent마다 state가 있고, 가장 급한 state가 tab과 workspace로 올라온다(rollup). Goto picker(`prefix+g`)는 모든 agent를 한 줄씩 보여 주고, Enter로 그 pane에 데려간다.**

## state

| state | 뜻 | 입력을 보내도 되나 |
| --- | --- | --- |
| `working` | 일하는 중 | 기다린다 |
| `blocked` | 승인이나 질문 화면 | 사람의 결정이 먼저 |
| `done` | 끝났고 아직 아무도 안 봄 | 예 |
| `idle` | 끝났거나 대기, 이미 봄 | 예 |
| `unknown` | agent는 있지만 분류하지 못함 | 화면을 먼저 본다 |

## 명령

1. 아래 "부트스트래핑 프롬프트"를 Write 도구로 `/tmp/tour-boot.txt`에 쓰고 `herdr agent prompt pm "$(cat /tmp/tour-boot.txt)"`(`--wait` 없이)
2. `herdr agent wait pm --until blocked --timeout 120000`: 질문 창이다.
3. 사용자: `prefix+g` -> `b` -> pm 줄에서 Enter -> 두 질문에 답한다(승인 창이면 이번만 승인) -> 원래 workspace로 돌아온다.
4. `herdr agent wait pm --until done --until idle --timeout 300000`: 떠나 있었다면 `done`, 보고 있었다면 `idle`
5. `cat ~/herdr-demo/PLAN.md`. 사용자가 `demo`의 `개발` 탭을 열면 `herdr agent get pm`이 `idle`

## 부트스트래핑 프롬프트

pm은 고르고 `PLAN.md`로 남기기만 한다. 만드는 건 `m1-pm`이다.

```text
나를 부트스트래핑할 작은 도구 하나를 골라 ~/herdr-demo/PLAN.md로 정리해.
부트스트래핑 도구는 내 일을 대신하지 않아. 내가 일하고 개선하는 방식을 더 빨리 개선하게 도와.
front, back과 3분 안에 만들 수 있는 크기로 추천해.

1. haiku 서브에이전트에게 ~/.claude의 memory와 최근 세션을 빠르게 훑게 해.
2. request_user_input으로 도구 후보 3~4개를 추천해.
3. 고른 도구에 필요한 축 3개를 request_user_input 한 번에 물어.
4. 답대로 PLAN.md를 써. 코드는 쓰지 마.
   # <도구 이름>
   목적, 축 셋과 답, back이 할 일, front가 할 일, 완료 조건
5. 다 쓰면 "PLAN.md 준비됨"으로 끝내.
```

## 참고

- `herdr agent list`: 모든 agent와 state. `herdr agent get <이름>`: 하나만
- `herdr agent focus <이름>`: 그 pane으로 가며 seen 처리
- `herdr agent attach <이름>`: agent 하나에만 전체 화면으로 붙는다(`prefix+q`로 나온다).
