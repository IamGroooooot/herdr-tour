---
name: p2-events
description: "herdr tour 고급 2/4: toast, 요약 줄, event 구독, plugin hook으로 끝나거나 막힐 때만 알게 한다."
---

1. 설정 파일을 백업하고, toast를 켜고, sidebar agent 행에 `$summary` 줄을 넣어 줘. `herdr server reload-config`로 바로 반영해.
2. 새 pane에서 socket에 직접 구독해서 pm, front, back의 상태 event가 흐르는 걸 보여 줘.
3. plugin에 `[[events]]` hook을 달아서, agent가 끝나면 걸린 시간을 `$summary` 줄에 남겨 줘. plugin은 `m3-plugin`에서 만든 것.
4. 내가 다른 workspace에 가 있는 동안 pm에게 작은 일을 시키고, toast와 요약 줄이 뜨는지 같이 봐.
