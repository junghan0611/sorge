# NEXT — sorge

> 이 집은 **메타 리포**다. 여기 적히는 것은 남의 집 일의 **상태**가 아니다 —
> 상태는 이슈 라벨에 살고 `./run.sh board` 가 보인다. 여기 적히는 것은 **다음 한 걸음**뿐이다.

# RAIL — 현재 좌표

- [x] **1. 집·계약·대장·첫 순회·이슈판·루프 계약·첫 무인 밤** — `CHANGELOG.md` `v2026.9.4` ·
      `v2026.9.8`(**절만 있고 태그·릴리즈 없음 — GLG 판정 대기**)
- [x] **2. 모양이 정해졌다 — 크로스 이슈 매니징** (`sorge#14`, GLG 2026-09-08)
- [x] **3. 상태가 문서를 떠나 이슈 라벨로 갔다** — `TRIAGE.md` 은퇴, `board` 가 판을 든다 (`2d2fca2` · `d898a39`)
- [ ] **4. GitHub Actions 라벨 레인** ← CURRENT: 이슈 개설이 Actions를 깨워 `sorge-bot`이 **라벨만** 단다. Copilot 아님
- [ ] **5. oracle 스위퍼 (pi extension)** ← PAUSED: 4가 산 뒤에 준비. RobOMP는 참고(웹훅·dedup·큐·host tool 경계), **omp fork 금지**. 호스트 풀에이전트는 `#28`

현재 좌표: 3 완료 → **4 Actions 라벨** → 5 스위퍼 준비(4 이후)

# NOW

- **Current:** 대문은 GitHub다. Forge를 ingress로 쓰자는 후보는 접었다. 라벨 레인은 호스트 RobOMP가 아니라 Actions다.
- **Next:** (1) `sorge`에 `issues.opened|reopened` 워크플로 — 리포 체크아웃·호스트 홈 없음. 이슈 JSON만 → 모델 한 방 → `sorge-bot` PAT로 라벨 PATCH. 댓글·PR·close 없음. `priority:`/`brief:`는 추측하지 않는다.
  → (2) sorge 한 집에서 실측(라벨 생김, 댓글 0)한 뒤, 대장 집으로 워크플로를 복제할지 재사용 워크플로로 묶을지 고른다.
  → (3) 4가 산 뒤에야 **5 준비**: oracle에서 pi extension 스위퍼. 참고는 RobOMP(llmlog `20260915T105735`)와 clawsweeper의 리뷰/적용 자격 분리. 상자는 봇 크리덴셜만. write를 라벨 너머로 바로 열지 않는다.
- **Blocker:** 4번 없음. `#28`은 5번의 풀도구·호스트 실행을 막는다. Copilot 레일 금지.
- **Read:** `labels.py` 헤더 · `LOOP.md` · llmlog `denote:20260915T105735` · `sorge#28`(5번 경계). 모델 기본값은 이미 있는 `deepseek/deepseek-flash`. 롤링 구독(GLM/Grok)으로 바꿀지는 4번 실측 때.
- **Do not touch:**
  - stock RobOMP 호스트 루프 재기동·15집 확장
  - `oh-my-pi` fork에 줄을 넣는 것
  - GitHub Copilot
  - Actions 레인에서 댓글·브랜치·PR·close
  - `priority:`/`brief:` 추측
  - 남의 리포에 커밋. **발견·명명·전달까지다**
  - 대장에 유도 가능한 사실. **판정만**
  - `agent-config`에 스킬 사본. 실물 하나, 나머지는 링크
  - Forge를 대문으로 세우기 (내부 백업은 열려 있으나 이번 레일 아님)

**손이 셋이고 권한이 다르다.** 사람 순회는 **라벨만** (`LOOP.md § never`). Actions 4번도 **라벨만**. 5번 스위퍼는 아직 없고, stock `sorge-bot` RobOMP는 꺼 둔다.

# RECENT

- **[2026-09-19] 대문을 GitHub로 되돌렸다.** herdr `akbash-bot`은 이슈 개설 ~3분에 라벨(댓글 없는 경우가 첫 스텝). clawsweeper는 라벨+리뷰+가드된 수리이고, 모델은 리뷰 중 write credential을 안 받는다. ogulcancelik `pi-extensions` / `agent-skills` / `herdr-plugin-github-start`는 라벨 봇이 아님 — 마지막 것은 보이는 형제 런처. GLG: Actions로 라벨 먼저, 스위퍼는 그다음 pi extension. Copilot 안 씀. Forge 대문 후보 접음.
- **[2026-09-15] 이슈판 lifecycle 기준점을 세웠다.** 미분류 대상 이슈 전부를 본문·thread로
  읽고 `ready|parked|proposed`와 `ball:`로 분류했다. `priority:`와 `brief:`는 GLG 순서와
  담당자 지침의 판정이라 추측해 쓰지 않았다.
- **[2026-09-15] 우리 요구를 벗고 stock 으로 갔다.** `sorge-label` 프로파일은 fork 버전업을
  막아서 버렸다. 라이브 증거 `sorge#25`. 설정은 `~/.config/sorge/robomp.env`에 남아
  모델은 `deepseek/deepseek-flash`. 호스트 루프는 `#28` 때문에 내렸다.

# 열린 물음

- Actions 워크플로를 sorge 한 집에만 둘지, 대장 집이 같은 재사용 워크플로를 부를지
- 라벨 모델: 미터 `deepseek-flash` vs 이미 내는 GLM/Grok 롤링
- `v2026.9.8` 태그/릴리즈 정합
- coord 이슈의 생애는 한 손만 잡는다 — `AGENTS.md`에 올릴지는 `guarded`
- 오라클과 리포 수가 다르다 (oracle 52 / thinkpad 71)
