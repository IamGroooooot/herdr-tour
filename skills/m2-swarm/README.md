# m2-swarm

개념도: [diagram.html](diagram.html)

**같은 repo를 worktree 여러 개로 나눠 agent들에게 동시에 맡긴다. worktree마다 작업 사본과 workspace가 따로라서 섞이지 않고, 끝은 완료 조건으로 확인한 뒤 고르거나 합친다.**

## 패턴

| 패턴 | worktree 수 | worktree마다 다른 것 | 끝내는 법 |
| --- | --- | --- | --- |
| Best-of-N | 2~3 | 같은 일, agent만 다르게(하나는 codex도 좋다) | 모두 같은 완료 조건으로 확인하고, 통과한 것 하나를 merge |
| Divide and Merge | 2~3 | 서로 다른 파일의 일. 공유 계약은 먼저 고정 | 하나씩 merge하고, merge마다 완료 조건 확인 |
| Nominal Group | 2~3 | 같은 질문(예: 완료 조건을 깨는 테스트)을 서로 못 보게 따로 | 전부 모아 중복만 빼고 merge |

## 명령

repo는 `~/herdr-demo`, worktree는 i = a, b, c다.

1. 시작점 commit: `git -C ~/herdr-demo add -A && git -C ~/herdr-demo commit -qm "m1 result"`
2. worktree마다 agent 띄우기: `herdr worktree create --cwd ~/herdr-demo --branch swarm/$i --label $i --no-focus` -> 응답의 `.result.root_pane.pane_id`(`<r_i>`)에 `herdr agent start s-$i --kind claude --pane <r_i> -- --permission-mode acceptEdits`(Best-of-N은 하나를 `--kind codex`로). `.result.workspace.workspace_id`는 정리할 때 쓰는 `<w_i>`
3. 동시에 맡기고 기다리기: worktree마다 `herdr agent prompt s-$i "<맡길 일>. commit은 하지 마" --wait --timeout 300000 &`, 그리고 `wait`
4. 확인하고 끝내기: worktree마다 commit -> 완료 조건 확인(`herdr worktree list`, `git diff --stat main swarm/$i`) -> 패턴의 끝내는 법대로 `git -C ~/herdr-demo merge --no-edit swarm/$i`
5. 정리: `herdr worktree remove --workspace <w_i> --force` -> `git -C ~/herdr-demo branch -D swarm/a swarm/b swarm/c`

## 참고

- 닫은 checkout 다시 열기: `herdr worktree open --cwd ~/herdr-demo --branch swarm/a`
