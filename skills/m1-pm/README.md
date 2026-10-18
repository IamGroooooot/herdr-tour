# m1-pm

개념도: [diagram.html](diagram.html)

**pm은 @front, @back에게 SendMessage로 맡기고, 결과를 완료 조건과 맞춰 본 뒤 디브리프를 남긴다. 투어 agent는 herdr로 pm의 state만 지켜보다가 막히면 골라 준다.**

## pm에게 줄 프롬프트

```text
앞에서 정한 ~/herdr-demo/PLAN.md의 도구를 @front와 @back과 함께 만들어.

1. 의도: PLAN.md의 목적과 완료 조건을 확인하고, 피해야 할 것을 한 줄 덧붙여. 결과가 달라질 결정이 남았을 때만 AskUserQuestion으로 한 번 묻고, 나머지는 근거를 들어 네가 정해.
2. 경계: @front 일과 @back 일을 서로의 결과를 몰라도 되게 나누고, 둘이 맞춰야 할 계약(interface)을 먼저 정해.
3. 브리핑: SendMessage로 둘에게 동시에 목적, 완료 조건, 계약, 막혔을 때 할 일을 보내고, 받은 계약을 한 줄로 되짚어 답하게 해. 끝나면 SendMessage로 알려 달라고 해.
4. 점검: 보고만 믿지 말고 실제 결과를 완료 조건과 맞춰 봐. 어긋난 부분만 맡은 쪽에 다시 보내고, 다시 보내는 건 두 번까지만.
5. 디브리프: 의도, 실제 결과, 차이가 난 이유, 다음에 바꿀 것을 PLAN.md 끝에 적고 세 줄로 보고해.
```

## 명령

1. 프롬프트를 `/tmp/tour-brief.txt`에 쓰고 보낸다: `herdr agent prompt pm "$(cat /tmp/tour-brief.txt)" --wait --timeout 540000`(Bash timeout 600000)
2. 돌아오면 state를 보고 이어 간다.
   - `blocked`: `herdr agent read pm --source visible`로 보고 가장 빨리 끝나는 쪽을 `herdr agent send-keys`로 고른다. front, back이 막혀도 같다.
   - `idle`인데 PLAN.md 끝에 디브리프가 없으면 아직 답을 기다리는 중이다: `herdr agent wait pm --until working` -> `herdr agent wait pm`
3. pm의 세 줄 보고와 확인 방법을 알려 준다.

## 참고: pane 명령과 agent 명령

pane 명령은 terminal에 글자를 그대로 쓰고 바로 돌아온다. agent 명령은 대상 agent를 확인하고 보내며, `--wait`이면 state 변화를 기다린다.

| 하고 싶은 일 | 명령 |
| --- | --- |
| shell 명령 실행(Enter 포함) | `herdr pane run <pane> '<명령>'` |
| Enter 없이 글자만 | `herdr pane send-text <pane> '<글자>'` |
| key 보내기 | `herdr pane send-keys <pane> enter`, `ctrl+c` |
| 출력 기다리기 | `herdr pane wait-output <pane> --regex '<패턴>'` |
| agent에게 일 맡기기 | `herdr agent prompt <이름> "<일>" --wait` |
| agent 화면에 key | `herdr agent send-keys <이름> esc` |
| agent state 기다리기 | `herdr agent wait <이름> --until idle` |
