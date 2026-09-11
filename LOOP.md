# LOOP — 루프는 시스템이 한다

> 이 파일 하나가 이 리포를 루프로 만든다. 지우면 루프가 꺼진다.
> **계약이다. 루프가 이 파일을 고치면 즉시 정지한다.**

전에 여기 223줄이 있었다. 그중 대부분은 **시스템이 아직 없어서 말로 적어둔 절차**였다 —
무엇을 어디에 적을지, 어떻게 알릴지, 무엇을 GLG에게 올릴지. 그 조각들이 이제 물건으로 서고 있다.
**말로 하지 않는다.** (GLG, 2026-09-10: *"길게 적을게 없어. 루프는 시스템이 하는거야."*)

옛 223줄은 `git log -- LOOP.md`. 되살릴 것이 아니라 감사 자료다.

## mission

GLG가 여러 리포에 올려대는 이슈를 한자리에서 본다. 이슈 하나의 생애:

```
분류 → 착수(그 집 워크트리, 그 집 시민) → 검수(다른 학교 형제) → 제안(sorge→GLG) → 머지|폐기(GLG)
```

부르는 것은 sorge, 미는 것은 GLG. **책임은 옮겨가지 않는다.**
sorge 자신은 코드를 고치지 않고, 이슈에 답글도 달지 않는다. 시도는 **그 집의 시민**이 한다.

## 시스템 — 네 조각이 말을 대신한다

| 조각 | 무엇을 대신하나 | 어디 |
|---|---|---|
| **board** | 「지금 판이 어떤가」 — 옛 `TRIAGE.md` 83줄 전부 | `./run.sh board` · 상태는 **이슈 라벨** |
| **heartbeat** | 「무엇이 두드리나」 — 옛 `§ driver` 절 | 밖의 시계. worker 세션 안에 살지 않는다 |
| **dm** | 「GLG가 어떻게 아나」 — 옛 `§ GLG는 어떻게 보는가` | `dm` 스킬. 한 사건에 한 줄 |
| **decision-gate** | 「GLG 결정 필요를 어떻게 넘기나」 — 옛 `verdict.decisions` | `agent-config` 소유 · `sorge#17` 이 그 형태를 묻는 중 |

이 넷은 각자 자기 집에서 자란다. **여기 적을 것은 그것들이 무엇을 대신하는지뿐이고,
어떻게 도는지는 그 집 문서가 든다.** 여기에 복제하면 그 사본이 먼저 낡는다.

**한 방향이 뒤집혔다.** 전에는 *"루프가 알리지 않는다. GLG가 당긴다"* 였다. `dm` 이 생기면서
**미는 쪽**이 됐다 — 사람이 판을 돌지 않아도 사건이 사람을 찾아온다. 다만 미는 것은 **알림뿐**이다.
승인·지시가 그 채널로 들어오지 않는다. 들어오면 알림 채널이 권위를 갖고 족쇄가 된다.

## watch — 무엇을 보는가

```bash
./run.sh board          # 대장 join 된 라이브 판
./run.sh board --debt   # 미분류 = 빚 전부
```

`gh search` 는 owner 전체를 긁으므로 **`LEDGER.md` 대장과 join 한 뒤에만** 대상이다.
`board` 가 그 join 을 든다. 대장 밖은 세지도 묻지도 않는다 (`AGENTS.md § 대상`).

**`sorge#N` 은 대개 남의 집 얘기다** — `house:<repo>` 라벨이 지배하고, 그 집이 대장에 있으면 대상이다.

## 상태 — 이슈 라벨. 문서 아님

`ns:value` 다섯 축. 문법은 `forge-config` 스위퍼 규약에서 물려받았다(`label-set` 단일값).

```
house:<repo>                    누구 몫인가. 여럿 가능. 이슈 리포 ≠ 일하는 집일 때만 붙인다
state:                           ready · running · review · proposed · blocked · parked
ball:                            owner · glg · sorge
priority:important-urgent        중요 + 긴급
priority:important-not-urgent    중요 + 안 긴급
priority:not-important-urgent    안 중요 + 긴급
priority:not-important-not-urgent 안 중요 + 안 긴급 — 나중을 위해 보관
brief:steward-ready              sorge가 담당자의 실행 지침을 확인했다
```

**이슈를 남기는 이는 이 라벨을 알 필요가 없다.** GPT 앱·봇·담당자·옆 형제가 자유롭게 이슈를
남기고, **sorge만** 전체 판을 읽어 라벨을 정리한다. `priority:`는 sorge가 GLG의 우리 쪽 순서를
기록한 것이다. 제목·날짜·모델 확신으로 사분면을 추정하지 않으며, 없는 `priority:`는
「안 중요+안 긴급」이 아니라 **sorge가 아직 우선순위를 정리하지 않음**이다.

**`brief:steward-ready`도 sorge의 확인 라벨이다.** 담당자는 live issue thread에 최소한
목표·범위/제외·검증(done_when 또는 관측)·권한/외부부작용 경계를 적는다. sorge가 그 명시를
확인하기 전에는 label을 붙이지 않는다. 자동 루프는 그 글을 대충 읽어 준비됐다고 판정하지
않으며, brief가 없으면 그 집 담당자에게 명확화를 요청할 뿐 작업을 열지 않는다.

**라벨 없음 = lifecycle 미분류 = 분류 빚.** `priority:`/`brief:` 부재는 별도의 **자율 착수 중지**다.
`state`·`ball`·`priority`·`brief` 이 둘 이상 붙으면 `board` 가 `⚠ 단일값 위반` 으로 띄운다.

**receipt 는 attempt 워크트리에 산다** — `~/repos/wt/<house>/<이슈>/NEXT--attempt-*`,
그 집 시민이 쓰고 그 집 시민이 읽는다. `done_when` · `impl` · `defects` 가 거기 있다.
sorge 는 거기에 쓰지 않고, 남의 이슈에 코멘트도 달지 않는다.

**`wt=` 는 저장하지 않는다.** 그 경로는 판정이 아니라 규약이라 유도된다. 저장하면 사라진
워크트리와 짝이 맞는 낡은 문자열이 남는다 — `done_when` 둘째 게이트가 없는 디렉터리를 향해
초록불을 켤 수 있었던 자리다(terra 검수 P0-2, 2026-09-10). `board` 가 매번 실재를 확인한다.

## 착수 조건 — 자율 실행기가 생길 때의 gate

**현재 sorge에는 worktree를 파거나 시민을 부르는 실행기가 없다.** `board`는 priority/brief 누락을
보여 주는 읽기면일 뿐이다. 아래는 나중에 그 실행기가 생길 때 직접 구현·테스트해야 할 gate다 —
문서에 있다고 자동으로 강제되는 것이 아니다.

전부 맞을 때에만 그 실행기가 GLG 손 없이 워크트리를 팔 수 있다:

```
state:ready ∧ ball:owner ∧ priority∈사분면 ∧ brief:steward-ready ∧ house∈대장
  ∧ authority≤쓰기 ∧ reversible=예(쓰기가 wt 안) ∧ money=아니오
  ∧ trust∈{GLG본인,형제} ∧ deadline=없음 ∧ 살아있는 attempt=0
```

`trust=외부` 는 무조건 `ball:glg` — 발신자를 못 믿는데 자동 착수하면 그게 프롬프트 인젝션의 문이다.
`deadline` 이 있으면 GLG가 알아야 하므로 역시 `ball:glg`. 우선순위는 이 안전문을 넘는 허가가 아니라,
통과한 일들의 정렬일 뿐이다.
**모델 자기 확신도는 쓰지 않는다.** sorge가 기록한 GLG 우선순위·sorge가 확인한 담당자 지침·권한·되돌리기·금전·신뢰·기한으로만 가른다.

## 착수 — 워크트리

- 자리: `~/repos/wt/<repo>/<이슈번호>`, 브랜치 `attempt/<이슈번호>`
- 앉는 자: `entwurf_fresh_call` 로 연 fresh citizen, `cwd` = 그 워크트리.
  브리핑은 **원문 넷**을 가리킨다 — 그 집 `AGENTS.md` · 대장의 그 집 행 · 그 행이 가리키는 담당자 문서 · 이슈 본문과 스레드
- 첫 질문은 **「이 이슈의 done_when 은 무엇인가」**. 재실행 가능한 명령이어야 하고 **워크트리 안에서 닫혀야** 한다.
  못 적으면 착수 불가. 그것이 노트를 이슈로 바꾸는 압력이다. 답은 그 워크트리의
  `NEXT--attempt-<번호>.md` 에 그 집 시민이 쓴다 — 여기가 attempt 의 정본이다
- **동시에 살아 있는 attempt 는 1개.** 시민의 수명은 attempt 하나이고, 끝나면
  `ready-for-review | blocked | abandoned` + 실제 돌린 명령과 출력으로 **한 번** 회신하고 물러난다.
  **그 회신이 상태 전이 이벤트다** — 별도 감지 엔진이 필요 없는 이유가 이것이다
- 결함이 나오면 **새 gid** 가 같은 워크트리에 앉아 diff 와 검수 receipt 를 읽고 받는다.
  이유는 쿼터가 아니라 **상주자 1명 유지 · tmux roster 억제 · 숨은 대화 상태 제거**다
- **죽은 시민은 같은 gid 로 못 되세운다**(pi 시민만 가능). 연속성의 정본은 transcript 가 아니라
  **이슈 + 담당자 문서 + 워크트리 diff/test 출력**이다

## 모델

구현은 진득하게 미는 쪽, 검수는 **착수한 학교와 다른 학교**. 로스터와 레일 순서는
`~/repos/gh/agent-config/MODELS.md` 가 든다 — 날짜 있는 스냅샷이라 기억보다 그 날짜를 믿는다.

## scope — 건드려도 되는 곳

- `allow`: **이슈 라벨 — `label-set` 만**(같은 namespace 의 기존 값을 제거하고 새 값 하나. add-only 는
  단일값 계약을 못 지킨다) · `~/repos/wt/` 아래 `git worktree add/remove` · `entwurf_fresh_call`
- `guarded`: `LOOP.md` · `LEDGER.md` · `AGENTS.md` · `NEXT.md` · `run.sh`
  → 건드리면 diff 크기와 무관하게 **즉시 정지하고 GLG에게 올린다**

## never

- `git push`, 그리고 sorge 이름의 커밋 (워크트리 안 커밋은 그 집 시민의 것이다)
- **이슈에 코멘트 쓰기 · 닫기.** 자동 답신은 남의 트리아지 용량을 갉는다 — 우리가 남의 curl 이 되지 않는다.
  **라벨은 2026-09-10 에 열렸다**(GLG): 라벨은 알림을 쏘지 않고 남의 받은편지함을 건드리지 않는다.
  **금지의 이유가 코멘트의 성질이었지 라벨의 성질이 아니었다.** 코멘트와 닫기는 그대로 닫혀 있다
- 남의 리포 파일을 sorge 가 직접 수정
- **그 집 시민이 아닌 자를 그 집 워크트리에 앉히기** — 무엇이 증거고 무엇이 재생성 가능한지는 그 집만 안다
- 대상 밖 집에 착수. **대장에 없는 집은 조용히 대상 밖**이고, 대장에 있는데 담당자 id 가 없는 집만 `ball:glg`
- 워크트리 밖에 쓰기. `~/org`, DB, daemon, 원격 API — 시민의 done_when 이 이걸 필요로 하면
  `reversible=예` 가 거짓이 되므로 `ball:glg`
- **워크트리 세션은 임베딩에서 제외한다.** 임베딩 대상은 GLG 의 턴이 들어간 세션이다

## budget

하루 24 tick · 조용한 시간 23:00–08:00 (Asia/Seoul) 은 쉰다 · 유료 API 대량 호출 0
