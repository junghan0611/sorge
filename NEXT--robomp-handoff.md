# NEXT — robomp 이슈 루프 인계 (2026-09-15 갱신, Claude Code / claude-opus-5)

**이 문서는 두 번 쓰였다.** 오전판은 「`sorge-label` 프로파일을 fork 에 얹고 fresh
라벨 봇을 만든다」였고, **오후에 GLG 가 그 전제를 폐기했다.** 오전판의 계획 절은
전부 무효다 — 실측 사실만 살아남았고 그건 아래에 남겼다.

## GLG 판정 (2026-09-15 오후)

> omp 를 수정하면 안돼. 그냥 써야돼. **그래야 omp 버전업을 할수가 있거든.**
> 그냥 omp robocomp 에서 제공하는 방식을 맞추자. **bg 도 오케이야.**
> 일단 만들어서 루프를 돌리게 하려는거야. **시작이 되야 튜닝을 할 수 있으니까.**
> run.sh 내가 켜고, 상태보고 끄고 가 되야돼.

무게는 「유지보수」가 아니라 **버전업**에 있다. fork 에 우리 줄이 있으면 상류를
따라갈 수 없고, 그때 잃는 것(계속 자라는 하네스)이 얻는 것(좁은 봇)보다 크다.

## 지금 상태

- **꺼져 있다.** `./run.sh robomp status` 로 확인. relay 훅 잔존 0
- **fork 는 상류와 동일하다.** `junghan0611/oh-my-pi` main = `f97fa5c`, 로컬 전용
  커밋 0. `git pull upstream main` 이 되고 현재 상류가 747줄 앞서 있다
- **폐기한 1,188줄은 곁가지에 있다** — `junghan0611/oh-my-pi@sorge-label-profile`.
  지우지 않은 이유는 그 판정이 틀려서가 아니라 아직 필요해지지 않아서다
- **우리 것은 손잡이 하나뿐** — `sorge@10f4a69`,
  `.claude/skills/sorge/scripts/robomp.py`

## 켜고 보고 끄기

```bash
cd ~/repos/gh/sorge
./run.sh robomp on          # dry-run — 무엇을 할지만 찍는다
./run.sh robomp on --go     # venv → env 파일 → gh-proxy → orchestrator → 훅 15개
./run.sh robomp status      # 포트·프로파일·모델·키·allowlist·훅 15줄
./run.sh robomp off         # SIGTERM → SIGKILL + relay 훅 삭제
./run.sh robomp judge owner/repo#NN   # 웹훅 없이 한 건만 큐에 넣는다
```

`DEEPSEEK_API_KEY` 가 셸에 없으면 `on` 이 사유를 대고 멈춘다(자식이 격리 XDG 라
호스트 구독을 못 본다 — 아래 §자격증명).

## 손잡이가 정하는 것은 셋뿐

**allowlist**(`board.ledger_houses()` 그대로, 대장 15집) · **모델** · **봇 이름**.
나머지 동작은 **stock 기본값에 맡긴다** — 값을 적는 순간 그것이 관리 대상이 되고,
버전업 때 기본값 변화를 못 따라간다.

예외 하나만 뒀다: `ROBOMP_QUESTION_AUTOCLOSE_ENABLED=false`. 무인으로 GLG 의
이슈를 닫는 것은 stock 기본값이어도 받지 않는다.

## 라이브 증거 — `sorge#25` (fork diff 0 줄)

```text
issues.opened(#25) → POST /webhook/github (HMAC 202)
  → INSERT OR IGNORE delivery dedup → claim
  → worktree farm/b9da13da/care-sorge-stock-full-agents
  → rpc_model_pick deepseek/deepseek-v4-pro thinking=high (resuming=False)
  → read / gh_search_issues ×2 / fetch_issue_thread
  → classify_issue → gh_post_comment → rpc_done (messages=4)
```

라벨 `question`,`triaged` + sorge-bot 댓글 1개. 판정 내용도 맞았다. 코드 수정·PR 은
사건이 요구하지 않아 하지 않았다. `on → status → off` 3박자 확인.

## 실측 사실 — 이 문서의 값은 여기다

### 자격증명 (pi/omp 공통 함정)

stock `robomp` 에는 **`agent_dir` 설정이 아예 없다.** 자식 omp 는 격리 XDG 로 뜨고
호스트 구독(`~/.omp/agent/agent.db`)을 못 본다. 오전에 이걸 symlink 로 이으려고
fork 를 고쳤는데, **모델을 바꾸면 코드가 필요 없다** — scrub 목록
(`worker.py:127-134`)은 `GITHUB_TOKEN`·`GITHUB_WEBHOOK_SECRET`·
`ROBOMP_REPLAY_TOKEN`·`ROBOMP_GH_PROXY_HMAC_KEY` 넷뿐이라 provider 키는 자식까지
전달된다.

2026-09-15 키 실측: **anthropic 401 · openai 401 · deepseek 200 · gemini 200.**
그리고 `XDG_DATA_HOME` 이 설정되면 omp 는 `PI_CODING_AGENT_DIR` 대신
`$XDG_DATA_HOME/omp/agent.db` 를 본다 — 이 우선순위가 오전의 함정이었다.

### 토큰 두 개, 역할이 다르다

- **`api/github/sorge-bot/pat`** (classic, `public_repo`) — 판정이 쓰는 것. 이슈·
  라벨·댓글·PR. fine-grained 는 **소유하지 않은 리포에 권한을 못 준다**(403
  `Resource not accessible by personal access token`) — collaborator 로 초대돼도
  그렇다. 그래서 classic 이다
- **`api/github/junghan0611/forge/pat`** (classic, `admin:repo_hook`) — `gh webhook
  forward` 전용. 훅 등록은 리포 소유자 권한이라 봇이 못 한다. **이 분리가 맞다**

### 도커 전용 가정이 호스트 배치에서 드러난 자리

RobOMP 는 도커 태생이라 `./data/...` 상대경로 기본값을 쓴다. 호스트에서는 `/data`
를 만들려 해 `PermissionError` 로 즉사한다 — 손잡이가 전부 절대경로로 덮는다
(`~/.local/share/sorge/robomp/...`). `gh-proxy` 는 `GITHUB_TOKEN` 을 들고,
orchestrator 는 **그 키가 env 에 있으면 기동을 거부한다**(`SystemExit`) — 그래서
env 파일이 둘이다.

### 라우팅

`issues.opened|reopened` 만 triage 를 깨운다. `labeled`/`edited` 는
`skip reason=issues.labeled ignored` — **자기깨움 루프가 구조적으로 없다.** 댓글·
PR 자기사건은 stock 이 이미 막는다(`github_events.py:346,202`). stock 에 이슈 생성
도구가 없으므로(`gh_post_comment`·`gh_push_branch`·`gh_open_pr`·`gh_request_review`·
`gh_search_issues` 뿐) 봇이 이슈를 만들 수도 없다.

## 튜닝 대기 — 루프가 도는 뒤에 잰다

1. **넓은 프로파일의 대가.** stock 은 댓글·브랜치·PR 까지 간다. 어디서 과했는지는
   라이브 사건이 모여야 안다. **좁히는 수단은 fork 가 아니라 프롬프트·라벨 규약·
   이슈 본문이어야 한다**
2. **사건 유실.** `gh webhook forward` 는 relay 훅 + 로컬 리스너다. 호스트가 꺼진
   동안의 사건은 잃고, **잃은 것을 모른다**(`sorge#24`). polling + 커서는 자동으로
   따라잡는다 — 재볼 후보
3. **one live judge.** 지금 세는 것은 in-process `_inflight`. 재기동 뒤 살아 있는
   judge 를 알아보는 방법이 없다
4. **보이는 창.** bg 를 받아들였으므로 지금은 창이 없다. 대화면이 필요해지면
   `entwurf_fresh_call` 이 그 자리다 — 그때도 권위는 라벨과 대장이고 창은 대화면일
   뿐이다

## 코드가 사는 곳

| 리포 | 커밋 | 무엇 |
|---|---|---|
| `junghan0611/sorge` | `10f4a69` | 손잡이를 stock 에 맞췄다 (프로파일 env 제거, deepseek, 키 점검) |
| `junghan0611/oh-my-pi` | `f97fa5c` = 상류 | **수정 없음.** 폐기분은 곁가지 `sorge-label-profile` |
| `junghan0611/agent-config` | `6914286` | OMP.md 운영 receipt (RobOMP 소스 사본 없음) |

## 열려 있는 이슈

- **`sorge#22`** — 이 판정으로 본문 전면 재작성됨. 정본은 거기다
- **`sorge#23`·`#24`** — 오전 라이브 사건 둘. `#24` 가 사건 유실 자리에 서 있다
- **`sorge#25`** — stock full 첫 사건. 이 인계의 증거
- **`sorge#19`** — 기억축 인터뷰. `judge` 로 손수 큐에 넣어 답이 달렸다

## 건드리지 말 것

- **fork 에 줄을 넣는 것.** 좁히고 싶으면 프롬프트·라벨 규약·이슈 본문으로 한다.
  fork 를 고치는 순간 버전업이 막힌다 — 그게 이 판정의 전부다
- **손잡이에 stock 설정값을 더 적는 것.** 기본값에 맡긴 것은 일부러 맡긴 것이다
- **`board.ledger_houses()` 를 우회한 allowlist.** 대장 파싱은 한 곳에만 있다
- **PAT 를 문서·repo·transcript 에 넣는 것.** password store 에만 둔다
