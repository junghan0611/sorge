# NEXT — sorge

> 이 집은 **메타 리포**다. 여기 적히는 것은 남의 집 일의 **상태**가 아니다 —
> 상태는 이슈 라벨에 살고 `./run.sh board` 가 보인다. 여기 적히는 것은 **다음 한 걸음**뿐이다.

# RAIL — 현재 좌표

- [x] **1. 집·계약·대장·첫 순회·이슈판·루프 계약·첫 무인 밤** — `CHANGELOG.md` `v2026.9.4` ·
      `v2026.9.8`(**절만 있고 태그·릴리즈 없음 — GLG 판정 대기**)
- [x] **2. 모양이 정해졌다 — 크로스 이슈 매니징** (`sorge#14`, GLG 2026-09-08)
- [x] **3. 상태가 문서를 떠나 이슈 라벨로 갔다** — `TRIAGE.md` 은퇴, `board` 가 판을 든다 (`2d2fca2` · `d898a39`)
- [ ] **4. 스킬로 환원한다** ← CURRENT: 이슈판의 기준점을 세웠다. 다음은 **공개 GitHub를 줄이고 Forge를 어떤 ingress로 쓸지** GLG가 고르는 일이다
- [ ] **5. 오토파일럿** ← PAUSED: 공개 이슈가 GLG 권한 agent를 깨우는 경계(`#28`)를 먼저 정해야 한다

현재 좌표: 3 완료 → **4 ingress·권한 경계 판정 대기** → 5 보류

# NOW

- **Current:** 이슈판의 lifecycle 기준점은 라벨로 내려앉았다. 현황 숫자는 저장하지 않고
  `./run.sh board`가 유도한다.
- **Next:** (1) **`sorge#28`에서 ingress·격리·secret topology를 GLG가 고른다.** 그 전에는
  GitHub public issue → full RobOMP turn을 다시 열지 않는다.
  → (2) GLG의 다음 검토: `forge.junghanacs.com`의 기존 Forgejo/`forge-config` 구조를 읽고,
  **자기 Forge를 내부 이슈판·봇 ingress로 쓸지**, GitHub는 공개 배포/제한된 면으로 남길지를
  가른다. 이 단계는 이관·새 봇 생성·GitHub 폐쇄가 아니라 구조와 권한의 판독이다.
  → (3) **버전업 리허설을 별도 워크트리에서 한다** — `upstream/main`이 `6f2c14b3`,
  우리 `f97fa5c`보다 **22,413 커밋 앞**이다(terra 실측). `pull` + venv deps 재설치가
  도는지 재보기 전에는 라이브 체크아웃에 pull을 섞지 않는다.
  → (4) `v2026.9.8` 태그/릴리즈 정합 판정 · board의 worktree/receipt 경고 전달.
- **Blocker:** **`sorge#28`** — public 이슈가 GLG 권한 턴을 깨운다. loop는 내렸고 15집
  확장은 보류다. Forge 검토는 이 문제를 피해 가는 전제가 아니라, 신뢰된 ingress를 어떻게
  둘지 고르는 별도 후보 판독이다.
- **Read:** `sorge#28` · `AGENTS.md` · `LOOP.md` · `labels.py` 헤더 · `forge-config`의
  기존 Forgejo 구조. 운전법은 담당자 문서 `denote:20260227T031800` §절차.
- **Do not touch:**
  - GitHub public issue → full RobOMP loop를 `#28` 결정 전에 재기동·확장
  - 남의 리포에 커밋. **발견·명명·전달까지다**
  - 대장에 유도 가능한 사실. **판정만**
  - `oh-my-pi` fork에 줄을 넣는 것. stock을 고쳐 경계를 우회하지 않는다
  - `agent-config`에 스킬 사본. 실물 하나, 나머지는 링크

**손이 둘이고 권한이 다르다.** 순회(사람이 부르는 sorge)는 여전히 **라벨만** 쓴다 —
코멘트·닫기는 닫혀 있다(`LOOP.md § never`). stock 루프의 `sorge-bot` 은 GLG 가
2026-09-15 에 stock 흐름을 그대로 받아들여 **댓글·브랜치·PR 까지 열려 있다.** 둘을
같은 규칙으로 읽지 마라. 무인 close 는 양쪽 다 닫혀 있다
(`ROBOMP_QUESTION_AUTOCLOSE_ENABLED=false`).

# RECENT

- **[2026-09-15] 이슈판 lifecycle 기준점을 세웠다.** 미분류 대상 이슈 전부를 본문·thread로
  읽고 `ready|parked|proposed`와 `ball:`로 분류했다. `priority:`와 `brief:`는 GLG 순서와
  담당자 지침의 판정이라 추측해 쓰지 않았다. 확인은 `./run.sh board`: 미분류 0 · 단일값 위반 0.
  남은 worktree/receipt 경고는 라벨 결함이 아니라 그 집 attempt의 사실이다.
- **[2026-09-15] 우리 요구를 벗고 stock 으로 갔다.** 오전엔 `sorge-label` 프로파일을
  fork 에 얹어 「라벨만 쓰는 좁은 봇」을 만들었다(1,188줄). 오후에 GLG 가 뒤집었다 —
  *"omp 를 수정하면 안돼. 그래야 omp 버전업을 할수가 있거든."* fork main 을 상류
  `f97fa5c` 로 되돌리고 폐기분은 곁가지 `sorge-label-profile` 에 남겼다.
  **되돌리니 셋 다 필요 없었다**: 봇 이슈 skip 은 도달 불가(stock 에 이슈 생성 도구가
  없다), 프로파일 1,057줄은 좁히기, 자격증명 symlink 는 **모델 교체로 코드 0줄에 풀렸다**
  (설정으로 풀 것을 코드로 풀었던 것 — 이게 가장 아픈 종류다). 라이브 증거 `sorge#25`:
  사건 → HMAC 202 → dedup → worktree → fresh 턴 → 라벨 + 댓글 → `rpc_done`, fork diff 0.
  인계 문서 `NEXT--robomp-handoff.md` 는 삭제했다 — `LEDGER.md:118` 의 자기 규율대로
  **안 움직이는 것**(담당자 문서 §절차 · `sorge#22`)이 그 내용을 든다.
- **[2026-09-10] 상태면이 문서에서 라벨로 옮겨갔다.** `TRIAGE.md` 56,928 → 554 bytes,
  `LOOP.md` 223 → 128줄. 세 축(`house:` `state:` `ball:`), `label-set` 단일값.
  **라벨 없음 = 미분류 = 빚 전부** — 적을 게 없으니 낡을 수도 없다.
  `LOOP.md § never` 에서 **라벨만 열렸다**(GLG). 코멘트·닫기는 닫혀 있다.
- **[2026-09-10] 교차검수 열 건.** terra: 주석이 계약을 재해석할 수 없다 · receipt 를
  코멘트에 약속해놓고 코멘트는 금지였다(→ attempt 워크트리로) · `wt=` 는 저장하지 않는다(유도).
  agent-config: 배선이 아니라 **목차**가 빠졌다 · 리포 이름은 단어다(워드 경계) ·
  인자 필수면 버튼이 아니다(→ cwd 유추) · **판정이 내려앉을 자리가 없었다**(→ `--house` 지연 생성).
- **[2026-09-10] 물려진 주장 하나.** 「컨테이너용 빌드 산출물의 소유」는 횡단 발견이 아니었다 —
  `~/AGENTS.md:190-192` 가 이미 답하고 실물도 계약대로였다. **확인 없이 물려받아 이름 붙여 올렸고,
  그 프레이밍이 다른 형제의 전제로 세탁됐다.** 물린 receipt 를 여기 남긴다.

# 열린 물음

- **coord 이슈의 생애는 한 손만 잡는다** — agent-config 가 낸 규약. `AGENTS.md` 에 올릴 값이
  있어 보이나 `guarded` 라 GLG 판정이다. 다만 **형제가 유도할 수 있는 문장이면 안 적는 게 맞다**
- **순회 주기.** 지금은 GLG가 부를 때만. 루프의 주기와 혼동하지 않는다
- **오라클과 리포 수가 다르다** (oracle 52 / thinkpad 71)
