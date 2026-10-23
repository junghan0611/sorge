# NEXT — sorge

이 집은 메타 리포다. 이슈 상태는 라벨과 `./run.sh board`, 최신 계약은 live thread에 산다.
지금 이어갈 일은 **[#31](https://github.com/junghan0611/sorge/issues/31)의 workspace 발신함 대응**이다(2026-10-23 GLG 요청). 기존 Opus가 당분간 대응하며 Sonnet을 새로 부르지 않는다. 별도 실행기·서비스·RobOMP를 만들거나 켜지 않는다. #30 Cloudflare는 아래 좌표에서 보류하고 #28은 미해결로 둔다.

# RAIL — 현재 좌표

- [x] **1. 봇 인증·입구 확인** — 10/19 봇 ID·PAT `repo` 범위·private 발신함 읽기 측정.
- [x] **2. 구동 방식·스킬 보강** — 10/23 GLG 승인으로 기존 `sorge` skill에 inbox 절 추가. 운영자는 같은 Opus, 별도 폴러 없음.
- [x] **3. 독립 검토 → 수동 한 건 초안** — workspace-glgdot#1 gate·근거를 Opus/코디 대조, 원문 게시 없음.
- [ ] **4. 원문 응답·반복 가동** ← CURRENT: GLG가 원문 답변과 푸시 후 루프 시작을 승인. 정리·검토·커밋·푸시 후 Opus 첫 틱.

현재 좌표: 수동 검증 완료 → **푸시 후 가동 준비**. 원격 게시·루프 등록은 아직 하지 않았다. Entwurf 코디 전달은 추후 확장으로 미승인.

# NOW

- **Next:** 정리본을 Opus `20261019T123505-bfabac`가 최종 검토 → 요청된 커밋·푸시·도장 성공 → 같은 Opus에 시작 신호. `/sorge inbox`가 URL 없이 찾고 원문 답변 후 다음 wakeup을 등록한다. 허용 발신함은 스킬 표의 glgdot·bbot·mini, 운영자는 기존 Opus 하나. GLG의 후속 참여 요청에 따라 집을 추가하되 이름 패턴으로 넓히지 않는다.
- **Read:** `.claude/skills/sorge/SKILL.md` §inbox가 실행 계약. `LOOP.md` 손 권한·`AGENTS.md` 저자 규칙을 반영했다. `experiments/workspace-inbox/DESIGN.md`는 합의와 증거. 원문 내용은 비공개에 유지하고 결정 필요·대응 막힘만 사건당 DM 한 통.
- **Verify:** repo/author ID·private·제목/PR gate와 URL 없는 목록 발견은 코디/Opus 각 수동 측정. 시작 후 **봇 identity·댓글 URL·완료 마커로 다음 목록에서 제외·실제 다음 wakeup 접수**를 별도 확인한다. 예약 접수≠다음 틱 실행. `git diff --check`. self-paced는 재개 시 다시 시작, 7일 만료(공식 문서, 로컬 수명 실증 전).
- **Do not touch:** 별도 실행기·timer·stock RobOMP/라벨 Actions 가동, 코디 전달·새 형제 호출·허용 표 밖 대상 확대·자동 수선·PR·닫기. 이번 허용은 허용 발신함의 원문 첫 검토 응답과 기존 Opus 루프뿐.

# PAUSED — Cloudflare #30 재개 좌표

로컬 시작점 `fb71d3a`, 11/11 테스트; Paid 안내·양 호스트 namespace 목록 조회까지만. 원래 RAIL 4 인증·요청량 경계부터 재개한다. namespace/repo/Worker 생성·배포는 아직 하지 않았다.

- **자리:** `ssh oracle` → `/home/junghan/repos/gh/sorge`, `main`. pull은 깨끗한 tree에서 `--ff-only`만.
- **Next:** `experiments/cloudflare/worker.mjs`에 인증·요청량 경계를 붙인다.
  미인증/설정 누락/호출 상한 초과가 Artifacts에 닿지 않게 하고, CPU 상한도 작은 값으로 정한다.
  코드 검증 뒤 namespace/repo/Worker 생성·배포 dry-run을 제시하고 실행 범위를 확인한다.
- **Verify:** `node --test experiments/cloudflare/worker.test.mjs`.
  기존 SHA 고정·read-only 테스트를 유지하고, 거부 요청의 binding 호출 0건을 추가 검증한다.
  실제 연결 뒤에는 같은 SHA의 파일을 Git과 Artifacts에서 대조한다. dry-run/대역 통과를 LIVE로 올리지 않는다.
- **환경:** oracle에서 Node v24.18.1·cf·Wrangler 4.143.0 측정.
  공식 문서의 4.145.0 조건은 binding types 및 remote-dev Blob 반환이다.
  전역 버전 변경은 nixos-config 담당 범위이며, 현재 버전의 실제 배포 가능 여부는 미검증이다.
- **배포 후보:** Worker `sorge-code-snapshot`의 `workers.dev`, namespace `sorge-experiment`, repo `code-snapshot`.
  이름은 설정 후보이며 실제 자원은 아직 없다. 형제의 런타임·인증·기록은 각자 유지한다.
- **비용:** 사용자 확인으로 $10 usage-spend alert가 있다. 알림은 차단이 아니고 기본 $5 구독료와 별개다.
  작업/저장량이 무한히 늘지 않게 제한한다. 제한 구현은 아직 없다.
- **Read:** #30 본문+최신 댓글 → `experiments/cloudflare/README.md` → Worker·테스트.
  계정 조작은 `cloudflare` 스킬의 토큰 경로와 dry-run → 확인 → 실행 계약을 따른다.
- **Do not touch:** 현재 무인증 후보의 공개 배포, 비밀/토큰을 이슈·Git·출력에 넣기,
  무한 fork/재시도, 자동 머지, 형제 추가 호출의 무단 확대, 대장 대상 확대,
  Entwurf 본체 수정, 스킬 사본 설치, stock RobOMP/라벨 Actions 재기동.

# RECENT

- **2026-10-07, API receipt:** 토큰 갱신 후 thinkpad와 oracle에서
  `cf artifacts namespaces list --limit 5` 각각 exit 0 / `[]`. repo 읽기·쓰기나 Worker 실행을 증명하지 않는다.
- **2026-10-07, 검수·Git:** Opus 검수에서 cwd 테스트 결함 발견·수정. 루트와 `/tmp`에서 각각 11/11.
  로컬 preview는 thinkpad `tmux sorge-cf-preview` / `127.0.0.1:8787`에만 있고 oracle 서비스가 아니다.
- **2026-10-07, GitHub receipt:** #30 이관이 연습용 `label-issue`를 깨웠으나 DeepSeek 키 401로 종료.
  사용자 지시로 비활성화, workflow API의 `state=disabled_manually` 확인. Cloudflare 코드 CI 실패가 아니다.

# DORMANT — 별도 레인, 이번 실험으로 재개하지 않는다

- **sorge-bot 중앙 에이전트:** 2026-09-19 판정은 그대로다. 집마다 Actions를 설치하지 않고,
  oracle 중앙 깨움·pi extension·첫 능력 라벨. RobOMP는 참고, omp fork 금지.
  재개할 때 llmlog `denote:20260915T105735`, `sorge#28`, `LOOP.md`, `labels.py`를 읽는다.
  공개 입력 → 호스트 사용자 권한 풀에이전트는 #28 경계 때문에 닫혀 있다.
  웹훅/폴링·모델 선택은 미정. Forge ingress 후보는 접었고 Copilot은 쓰지 않는다.
- **기존 집의 기준점:** 첫 집/계약/대장/순회는 `CHANGELOG.md`의 `v2026.9.4`,
  크로스 이슈 매니징은 #14, 문서 상태판은 라벨/board로 이동(`2d2fca2`, `d898a39`).
  Actions #29는 한 집 연습으로 완료했으며 대장 집으로 복제하지 않는다.
- **남은 판정:** `v2026.9.8`은 CHANGELOG 절만 있고 태그/릴리즈 정합 판정이 남았다.
  coord 이슈 생애의 단일 손 규칙을 AGENTS.md에 올릴지는 guarded다.
