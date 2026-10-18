# p1-compose

개념도: [diagram.html](diagram.html)

**세 가지 결정을 조합해 나만의 agent team을 만들어 보자. 하위 작업끼리 서로의 결과를 몰라도 되나(Decomposition), agent 사이에 무엇이 흐르나(Communication), 여러 결과를 어떻게 하나로 모으나(Convergence).**

## 세 결정

| 결정 | 묻는 것 | 쓰게 되는 herdr 기능 |
| --- | --- | --- |
| Decomposition | 하위 작업끼리 서로의 결과를 몰라도 되나? | `herdr tab create`, `herdr pane split`, `herdr agent start`, `/rename` |
| Communication | agent끼리 context는 공유되지 않는다. 무엇으로 이어 줄까? | SendMessage, `herdr agent prompt`, 공유 파일을 `herdr pane run`으로 `tail -F` |
| Convergence | 여러 결과를 어떻게 하나로 모으고, 누가 확인하나? | `herdr agent wait`, `herdr agent read`, `--kind codex` verifier, `herdr pane wait-output` |

## 알아 두기

### Decomposition: 나눌 수 있을 때만 나눈다

- 하위 작업이 서로의 결과를 몰라도 될 때만 여럿이 하나보다 낫다. 서로 기다리거나 맞춰야 하면 조정 비용이 이득을 먹는다.
- 나누기 좋은 일: 웹 조사, 후보 수집, 독립 코드 리뷰, 테스트 생성. 하나에게 맡길 일: 한 모듈 리팩토링, 처음부터 끝까지 톤이 같아야 하는 긴 글.
- agent 수는 독립 하위 작업 수만큼. 단순한 일은 하나, 비교는 2~4개, 큰 조사만 그 이상이다. agent가 늘면 token 비용도 그만큼 는다.

### Communication: 넘기지 않은 건 모른다

- agent마다 새 context에서 시작한다. 넘겨준 지시와 돌려받는 요약이 전부다.
- 지시에는 목적, 출력 형식, 하지 말 것, 서로 맞춰야 할 계약을 적는다. 함께 보는 상태는 파일로 둔다.
- 받은 쪽이 계약을 한 줄로 되짚어 답하게 하면 어긋남을 일찍 잡는다.

### Convergence: 만드는 것보다 모으는 게 어렵다

- agent를 늘리면 결과물은 쉽게 늘지만, 틀린 조각은 합칠 때 섞이거나 커진다.
- 확인은 같은 걸 본 복제 agent보다 다른 정보나 기준을 가진 쪽이 한다. 다른 모델, 테스트, 실제 실행 결과 같은 것.
- 끝은 몇 번 돌았는지가 아니라 완료 조건을 통과했거나 정한 budget을 다 썼을 때다.

### 막히면 어느 결정을 다시 볼까

| 증상 | 다시 볼 결정 |
| --- | --- |
| 역할이 흐리다, 나누면 안 될 일을 나눴다 | Decomposition |
| 같은 일을 두 번 했다, 각자 다른 가정으로 만들었다 | Communication |
| 확인 없이 끝났다, 언제 끝낼지 모른다 | Convergence |
