---
name: b2-team
description: "herdr tour 초급 2/3: 인사 탭과 개발 탭에 claude와 codex 다섯을 띄워 팀을 차린다."
---

1. claude와 codex가 새 폴더 신뢰를 물으면 묻지 말고 네가 수락해 줘.
2. `~/herdr-demo`를 만들고 `git init -b main` 한 뒤, 거기서 새 workspace `demo`를 열어 줘.
3. 첫 탭은 `인사`. 왼쪽에 claude(`hi-claude`), 오른쪽에 codex(`hi-codex`)를 띄우고, claude가 herdr로 codex에게 직접 인사를 건넨 뒤 답을 읽게 해 줘.
4. 두 번째 탭은 `개발`. 왼쪽 큰 pane은 `pm`, 오른쪽 위는 `front`, 아래는 `back`. 셋 다 claude로 띄우고 herdr 이름과 클로드 세션 이름을 `/rename 세션명`으로 똑같이 붙여 줘.
5. 셋에게 역할을 알려 주고, front와 back은 SendMessage로 `@pm`에게 "준비됨"을 보고하게 해 줘.
