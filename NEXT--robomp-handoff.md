# NEXT — robomp 라벨 스위퍼 인계 (2026-09-15, Claude Code / claude-opus-5)

GLG 판정으로 **방향이 바뀌었다.** 아래는 오늘 만든 것 전부와, 왜 그것이 GLG가 원하는
모양이 아닌지, 그리고 다음 사람이 무엇을 다시 재야 하는지다.

## GLG의 새 요구 (2026-09-15, 이 문서가 쓰인 이유)

세 문장이 전부다.

1. **"bg로 도는 건 내가 원하는 방식이 아니다."** 백그라운드 데몬이 판정을 내면 GLG가
   그 판정자와 대화할 수 없다. 뒤에서 도는 것은 제한적이다.
2. **"나는 소넷을 불러서 그 친구가 깨어나서 하는 거야. 그래야 니가 그 친구랑 이야기를
   하는데."** 원하는 것은 **보이는 형제** — 깨어나서 판정하고, 그 자리에서 대화 가능한
   시민. entwurf가 이미 그 축을 든다(`entwurf_fresh_call` → 보이는 창).
3. **"omp 수정하는 것도 별로야. 유지보수하기 힘들어."** 상류(can1357/oh-my-pi)에서
   갈라진 fork를 계속 리베이스하며 사는 것이 부담이다. **"우리가 문을 열어놨으니까 pi
   에서 뭔가 익스텐션으로 처리가 간단하게 될지도 몰라."**

따라서 지금 서 있는 물건은 **작동하지만 채택되지 않은 선례**다. 지우지 않고, 무엇이
값이었고 무엇이 비용이었는지 남긴다.

## 지금 상태 — 꺼져 있다

`./run.sh robomp off` 를 돌렸다. gh-proxy·orchestrator·forward 15개 전부 내렸고,
**GitHub 쪽 relay 훅 15개도 삭제**했다(남기면 배달이 아무도 안 받는 곳으로 흐르고 다음
`on` 이 422로 죽는다). 설정 파일(`~/.config/sorge/robomp*.env`, 0600)과 데이터
(`~/.local/share/sorge/robomp/`)는 남아 있다. `./run.sh robomp on --go` 한 번으로 되살아난다.

## 오늘 실제로 작동한 것 (측정, oracle 호스트)

### 전 구간이 돌았다
```
issues.opened(junghan0611/sorge#24)
  → gh webhook forward → POST /webhook/github 202 (HMAC 검증)
  → SQLite delivery dedup → issue별 직렬 큐
  → git worktree farm/82f4aee8/… → fresh omp --mode rpc (sonnet-4-6, thinking=high)
  → fetch_issue_thread → set_issue_labels → rpc_done   (43초)
라벨: house:sorge · ball:glg · priority:important-not-urgent   댓글 0 커밋 0
봇 라벨의 되돌아온 웹훅 3건 → skip reason=issues.labeled caused by self
```

### 손으로도 돈다
`./run.sh robomp judge junghan0611/sorge#19` → `sorge-bot` 이
`house:sorge` + `house:agent-config` + `house:andenken` + `ball:sorge` + `priority:` 를 달았다.
**횡단 몫 셋을 정확히 짚었다**(그 이슈 제목이 "기억축 활용성 인터뷰 —
agent-config·andenken·OpenClaw"). `state:` 는 붙이지 않았다 — 아직 아무 일도 시작되지
않았으니 없는 것이 맞다.

### 봇 계정
`sorge-bot`, classic PAT + `public_repo` 스코프 하나(`pass api/github/sorge-bot/pat`).
대장 대상 **15/15** 집에 Write collaborator 로 초대·수락 완료. 무변경 PATCH 200 으로
라벨 쓰기 실제 확인.

## 다음 사람이 알아야 할 실측 사실 (여기가 이 문서의 값이다)

### 토큰
- **fine-grained PAT 는 발급 계정이 소유하지 않은 리포에 쓸 수 없다.** Write
  collaborator 여도 `403 Resource not accessible by personal access token`. 남의 리포에
  라벨을 쓰려면 **classic + `public_repo`** 여야 한다. 대상 15집 전부 public 이라 이
  스코프로 충분하다.
- 읽기는 신호가 아니다 — public 리포는 토큰 없이도 200 이다. **쓰기만 신호다.**
  무변경 PATCH(같은 값으로 라벨 수정) 한 번이 비파괴 권한 테스트다.
- `gh webhook forward` 는 `admin:repo_hook` 이 필요해 GLG 의 classic 토큰
  (`pass api/github/junghan0611/forge/pat`)을 쓴다. 봇 토큰과 섞지 않는다.
- `pass api/anthropic/junghanacs` **API 키는 죽어 있다(401)**.

### 모델 자격증명 (pi/omp 공통 함정)
자식 omp 프로세스에 workspace별 격리 XDG 를 주면, **`XDG_DATA_HOME` 이 설정된 순간
`PI_CODING_AGENT_DIR` 오버라이드가 자격증명 저장소에 대해 무시된다.** 자식은
`$XDG_DATA_HOME/omp/agent.db` 를 보고 "No API key found for anthropic" 로 죽는다.
호스트 `~/.omp/agent/agent.db` 를 그 자리에 **심링크**하면 세션·blob·캐시 격리는
유지한 채 GLG 구독 자격으로 sonnet 이 돈다. 이것이 죽은 API 키를 우회한 유일한 길이었다.

### 도커 전용 가정이 호스트 배치에서 드러난 자리
- `ROBOMP_WORKSPACE_ROOT`/`SQLITE_PATH`/`LOG_DIR`/`NATIVES_CACHE_ROOT` 는 **절대경로**
  여야 한다. 상대경로면 `git worktree add` 가 pool cwd 기준으로 풀려
  `fatal: already exists` 로 죽는다.
- `robomp serve` 는 `GITHUB_TOKEN` 이 환경에 보이면 **시작을 거부한다**
  (`python/robomp/src/server.py:261`). PAT 는 gh-proxy 사이드카만 든다 → 항상 2프로세스.
- `gh webhook forward` 는 리포에 relay 훅을 만들고 프로세스가 죽어도 남긴다.
- 리포 안 `python/robomp/.env` 를 두면 `Settings` 테스트 4건이 그 값을 읽어 깨진다.

### 라우팅
`route()` 가 사건을 통과시켜도 dispatcher 에 분기가 없으면 `no-op dispatch` 로 조용히
사라진다(`issues.labeled|edited` 가 그랬다). **"깨운다"를 라우팅으로 결론내지 말고
`rpc_start` 까지 로그로 확인해야 한다.**

## 무엇이 값이었고 무엇이 과했나

라벨 판정 턴이 실제로 쓴 도구는 **`fetch_issue_thread` + `set_issue_labels` 둘뿐**이고
리포 체크아웃은 한 줄도 읽지 않았다. 그런데 RobOMP 는 그 두 번을 위해 매번 워크트리를
파고 의존성까지 깔았다. **라벨만이면 과한 도구다.**

RobOMP 가 값을 내는 자리는 그 다음이다 — 같은 날 시험 리포(`junghan0611/robomp-lab`)에서
stock 프로파일은 이슈 하나를 받아 분류→라벨→댓글→브랜치 푸시→**PR #2** 까지 갔다.
delivery 기준 중복 제거 · issue별 직렬 큐 · 백오프 재시도(3회째에 살아난 사건 있음) ·
사건별 워크트리 격리 · host tool 감사 경계 · orchestrator 가 PAT 를 아예 못 보는 구조가
그 능력을 받친다. 그건 GitHub Actions 한 스텝으로 만들 수 없다.

**그러나 GLG 가 원하는 것은 그 능력이 아니었다.** 원하는 것은 대화 가능한 보이는 형제다.
그 축에서 보면 RobOMP 의 강점(견고한 무인 큐)은 바로 약점이다 — 무인이라 대화면이 없다.

## 다음 사람이 재봐야 할 것 — pi 익스텐션 방향

GLG 가 가리킨 방향: **pi 쪽 익스텐션으로 간단히 될지도 모른다.**

재볼 것:
1. pi 익스텐션/훅(`--hook`, `-e/--extension`)이 **외부 사건으로 턴을 깨울 수 있는가**,
   아니면 이미 도는 세션 안에서만 사는가. 후자라면 사건 수신은 여전히 밖에 있어야 한다.
2. 사건 수신을 가장 얇게 만드는 법. GitHub 이슈 웹훅을 받는 최소 표면은 무엇이고, 그것이
   **보이는 형제를 깨우는 것**(`entwurf_fresh_call`)으로 바로 이어질 수 있는가.
   entwurf 는 이미 "보이는 창 + 콜백 + garden id" 를 든다 — 사건 → `entwurf_fresh_call` →
   그 창에서 판정 → GLG 가 그 창과 대화. 이 모양이 GLG 요구와 정확히 맞는다.
3. 그러면 남는 질문은 **누가 웹훅을 받아 entwurf 를 호출하는가** 하나로 줄어든다.
   RobOMP 전체(HMAC·dedup·큐·워크트리·RPC)가 아니라 그 앞단 한 조각만 필요하다.
4. **fork 유지보수 비용을 지지 않는 배치**여야 한다. 오늘 fork 에 넣은 것은
   `sorge-label` 프로파일(env 게이트 뒤, `full` 무회귀)이지만, 상류와 갈라진 축이
   하나 늘어난 것은 사실이다.

## 코드가 사는 곳 (전부 main 에 푸시됨)

| 자리 | 커밋 | 내용 |
|---|---|---|
| `junghan0611/oh-my-pi` (fork, remote `glg`) | `6519adb` `84a2766` | 봇 작성 이슈 skip 복구 + `sorge-label` 프로파일(fresh 턴·도구 넷·self-wake 차단·coalescing·`ROBOMP_AGENT_DIR`) |
| `junghan0611/sorge` | `21b606d` `52f15e3` | `.claude/skills/sorge/scripts/robomp.py` — `on/off/status/allowlist/judge` |
| `junghan0611/agent-config` | `6914286` | `OMP.md` 2026-09-15 절 — 도입 profile·activation 조건·운영 receipt |
| 담당자 문서 `20260227T031800` | — | 현재 보고 + `:noexport:` 절차(함정 6건 포함) |

검증: robomp 스위트 716 passed(유일 실패 `test_run_git_kills_hung_child` 는 우리 커밋이
건드리지 않은 기존 flake) · ruff clean.

## 열려 있는 이슈

- `sorge#22` — autopilot(memento). 이 일의 본줄. `state:ready` `ball:sorge`.
- `sorge#23` — 봇 계정 도입과 초대 확장 (초대는 15/15 완료됨, 문서 갱신 필요)
- `sorge#24` — 공개 webhook ingress 없이 이 호스트가 꺼지면 사건도 끊긴다

## 건드리지 말 것

- 대장 파싱을 다시 구현하는 것 — `board.ledger_houses()` 하나뿐이다.
- `sorge-label` 프로파일에 댓글·PR·push·`entwurf_fresh_call` 도구를 넣는 것.
  `LOOP.md § 착수 조건` 의 열 조건 게이트 없이 그것을 넣으면 **이슈 본문이 곧 실행
  권한**이 된다 — 프롬프트 인젝션의 문이다.
- 비밀값을 리포 안 파일에 쓰는 것. `pass` → 0600 env 파일만.
