# NEXT — sorge

이 집은 메타 리포다. 이슈 상태는 라벨과 `./run.sh board`, 최신 계약은 live thread에 산다.
지금 이어갈 일은 **[sorge#30](https://github.com/junghan0611/sorge/issues/30)**의 Cloudflare 협업 실험이다.
**기존 sorge-bot과 별개다.** 자세한 이유·실측은 이슈에 두고 여기에는 다음 한 걸음만 둔다.

# RAIL — 현재 좌표

- [x] **1. 문제와 자리** — entwurf#131 → sorge#30. 독립 형제의 동시 변경·검토·선택을 실제로 실험한다.
- [x] **2. 로컬 시작점·독립 검수** — `fb71d3a`, `experiments/cloudflare/`, 테스트 11/11. Artifacts LIVE 증거는 아니다.
- [x] **3. 구독·API 입구** — 사용자 Workers Paid 결제 확인. thinkpad·oracle namespace 목록 조회 성공(`[]`).
- [ ] **4. 보호된 Worker → 실제 Artifacts → 작은 배포** ← CURRENT: oracle에서 인증·요청량 경계부터
- [ ] **5. 실제 형제 협업** — 변경 후보·겹침·독립 검토·선택을 한 바퀴 돌고 필요한 접점을 발견한다.

현재 좌표: 3 입구 확인 → **4 준비**. namespace/repo/Worker 생성·배포는 아직 하지 않았다.

# NOW

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
  Entwurf 본체 수정, 스킬 사본 설치, sorge-bot/라벨 Actions 재기동.

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
