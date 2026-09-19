# NEXT — sorge

> 이 집은 **메타 리포**다. 여기 적히는 것은 남의 집 일의 **상태**가 아니다 —
> 상태는 이슈 라벨에 살고 `./run.sh board` 가 보인다. 여기 적히는 것은 **다음 한 걸음**뿐이다.

# RAIL — 현재 좌표

- [x] **1. 집·계약·대장·첫 순회·이슈판·루프 계약·첫 무인 밤** — `CHANGELOG.md` `v2026.9.4` ·
      `v2026.9.8`(**절만 있고 태그·릴리즈 없음 — GLG 판정 대기**)
- [x] **2. 모양이 정해졌다 — 크로스 이슈 매니징** (`sorge#14`, GLG 2026-09-08)
- [x] **3. 상태가 문서를 떠나 이슈 라벨로 갔다** — `TRIAGE.md` 은퇴, `board` 가 판을 든다 (`2d2fca2` · `d898a39`)
- [x] **4. Actions 라벨 연습** — sorge 한 집만. `#29` 실측: `sorge-bot`이 `state:ready`·`ball:glg`, 댓글 0. **대장에 복제하지 않는다** (GLG 2026-09-19)
- [ ] **5. sorge-bot 중앙 에이전트** ← CURRENT: 깨움은 이 집 하나. 대장 이슈가 sorge로 모인다. oracle에서 pi extension. RobOMP는 참고, omp fork 금지

현재 좌표: 4 연습 완료 → **5 중앙 에이전트**

# NOW

- **Current:** 이 리포가 `sorge-bot`의 현현이다. 돌봄은 집마다 워크플로를 심는 일이 아니다. Actions `#29`는 라벨 PATCH가 되는지만 본 연습이다. 필요한 것은 에이전트 — 그래서 RobOMP를 찾았던 것이다.
- **Next:** (1) oracle 중앙 깨움 설계 — 대장 allowlist, 봇 PAT, 이슈 JSON만. 집마다 `.github/workflows` 금지.
  → (2) 손: pi extension. 참고는 RobOMP(웹훅·dedup·큐·host tool 경계, llmlog `20260915T105735`)와 clawsweeper의 리뷰/적용 자격 분리. **omp를 고치지 않는다.**
  → (3) 첫 능력은 라벨(연습에서 검증된 두께). 댓글·브랜치·PR은 자격 가른 뒤에.
- **Blocker:** `#28`은 호스트 GLG uid 풀에이전트를 막는다. 중앙 봇은 상자·봇 크리덴셜·도구 화이트리스트로 그 경계를 지킨다. Copilot 금지.
- **Read:** llmlog `denote:20260915T105735` · `sorge#28` · `LOOP.md` · `labels.py` 헤더 · 연습물 `.github/workflows/label-issue.yml`(복제 원본 아님)
- **Do not touch:**
  - 대장 집에 Actions 워크플로를 심는 것 — 1번 스타일, 접었다
  - stock RobOMP 호스트 루프를 그대로 재기동·15집 확장
  - `oh-my-pi` fork에 줄을 넣는 것
  - GitHub Copilot
  - `priority:`/`brief:` 추측
  - 남의 리포에 커밋. **발견·명명·전달까지다**
  - 대장에 유도 가능한 사실. **판정만**
  - `agent-config`에 스킬 사본. 실물 하나, 나머지는 링크
  - Forge를 대문으로 세우기

**손이 둘이다.** 사람 순회는 **라벨만**. 중앙 `sorge-bot`은 이 집의 에이전트이고, 첫 두께는 라벨이다. 연습용 Actions는 sorge에만 남는다.

# RECENT

- **[2026-09-19] 줄기는 중앙 에이전트다.** Actions `#29` 통과 뒤 GLG: 1번은 여기 연습으로 끝, 2번이 돌봄이다. 깨움은 sorge 하나. 집마다 워크플로를 심지 않는다. 필요한 것은 에이전트.
- **[2026-09-19] 대문을 GitHub로 되돌렸다.** Forge ingress 후보 접음. Copilot 안 씀.
- **[2026-09-15] 이슈판 lifecycle 기준점.** `priority:`/`brief:`는 추측하지 않는다. `sorge-label` 프로파일은 omp 버전업을 막아 버렸다. 호스트 루프는 `#28` 때문에 내렸다.

# 열린 물음

- 중앙 깨움: 웹훅 한 점 vs 폴링 (RobOMP는 웹훅이었다)
- 라벨 모델: 미터 DeepSeek vs 이미 내는 GLM/Grok 롤링
- `v2026.9.8` 태그/릴리즈 정합
- coord 이슈의 생애는 한 손만 잡는다 — `AGENTS.md`에 올릴지는 `guarded`
