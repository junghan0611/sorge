# TRIAGE — 이슈 트리아지 원장

> `LOOP.md`가 계약이다. 이 파일은 그 계약이 쓰는 유일한 쓰기 대상(`allow`).
> 두 절, 규율이 다르다: **이슈** 절은 *현재 판(mutable projection)* — 한 이슈 = 한 줄, 제자리에서 갱신.
> **tick log** 절은 *append-only 이력* — 한 tick = 한 블록, 끝에만 붙인다.
> `done_when` 측정은 이슈 절의 첫 칼럼(`repo#번호`) 집합과 `wt=` 실재만 본다 — tick log는 안 본다.

## 형식을 이렇게 고른 이유

79개, 나중엔 수백 개가 쌓인다는 전제로 세 가지를 기준 삼았다.

1. **grep이 먼저다, 사람 눈은 그다음이다.** 8칸 마크다운 표는 GitHub에서는 읽히지만
   `cat`/`tail`로 보는 터미널에서는 폭이 넘쳐 줄바꿈된다. `key=value` 한 줄이면
   `grep sorge#5 TRIAGE.md`, `grep verdict=GLG TRIAGE.md` 가 그대로 통한다.
2. **`done_when`이 재실행 가능한 명령이라고 했으니, 이 파일도 명령이 파싱하기 쉬운 모양이어야
   한다.** 탭으로 가른 첫 필드(`repo#번호`)만 뽑으면 집합 연산이 된다 — 표라면 마크다운
   파서가 필요하다.
3. **한 줄 = 한 이슈면 diff가 이슈 단위로 난다.** 표는 한 줄 끼워 넣으면 위아래 셀 정렬이
   같이 흔들릴 때가 있다(도구에 따라). 새 이슈는 절 끝에 붙고, 있는 줄은 제자리에서 바뀐다.

## 이슈

```
repo#번호	house=... kind=... authority=... reversible=... money=... trust=... deadline=... ball=... verdict=... state=... [wt=... impl=... done_when=...]
```

`house` 는 **워크트리가 속하고 담당자 문서가 대장에 배정된 집**이지 이슈가 걸린 리포가 아니다 — `sorge#N` 은
대개 남의 집 얘기다. `state` 만 전이하고 `wt`·`impl`·`done_when` 은 attempt 가 닫힐 때까지 불변(`LOOP.md § 분류 축`).

junghan0611/sorge#5	house=doomemacs-config(배정, 곁노트:이슈는 sorge에 걸렸고 측정은 doomemacs-config·환경은 nixos-config) kind=운영 authority=읽기 reversible=예 money=아니오 trust=GLG계정(본문 "not GLG direct") deadline=없음 ball=담당자 verdict=담당자몫 state=분류
junghan0611/sorge#4	house=garden(대상 밖 — 대장에 없음) kind=버그 authority=쓰기 reversible=예 money=아니오 trust=외부(gpt-6-astra 지적, GLG계정으로 이슈화) deadline=없음 ball=담당자 verdict=보류(대상 아님 — GLG가 garden을 대장에 올리면 다시 뜬다) state=분류
junghan0611/sorge#1	house=sorge(배정, 곁노트:andenken·nixos-config 3집 계약) kind=운영 authority=쓰기 reversible=예 money=아니오 trust=GLG계정(claude-opus-5 정정, 2026-09-06) deadline=없음 ball=GLG verdict=GLG결정필요(3집 권한경계 확정이 본문 자체 요청) state=분류
junghan0611/agent-config#23	house=미배정(LEDGER에 agent-config 줄 없음) kind=기능 authority=쓰기 reversible=예(LOOP.md 지우면 루프 꺼짐) money=아니오(예산 0 명시) trust=GLG계정(claude-opus-5 작성, 2026-09-07) deadline=없음 ball=GLG verdict=GLG결정필요(미배정 + 자기지시적: 이 루프 자체의 설계 이슈) state=분류
junghan0611/doomemacs-config#11	house=doomemacs-config(배정, GLG 확정 2026-09-07) kind=버그 authority=쓰기 reversible=예(쓰기 wt 안 — 브리핑에 실데이터·daemon 무접촉 명시) money=아니오 trust=형제(claude-opus-5 작성, GLG 계정) deadline=없음 ball=담당자 verdict=담당자몫 state=검수 commit=2d53238 impl_reply=ready-for-review@20:20 impl_retired=20:20 review=20260907T202141-ce4a0c@openai-codex/gpt-5.6-sol(착석 20:21, verdict=defect@20:26, 물러남) defects="①#+signature: 빈 값 의미(삭제 vs placeholder) 미정 — 코드는 주입, docstring은 미주입 약속, 테스트 없음 ②rename 권한은 파일명만(agent-server.el:274-283)인데 이 손은 rename이 본문에 #+signature: 줄을 쓰게 함 — 권한 계약 확대" defects_kind=둘다GLG결정 verified_clean="cl-letf 범위·에러복원 OK / bulk skip 유지 OK / 실데이터 누수 없음 / 102/102 재측정" wt=~/repos/wt/doomemacs-config/11 impl=20260907T201133-7972a1@claude-code/opus done_when="cd ~/repos/wt/doomemacs-config/11 && ./tests/run-tests.sh → Ran 1NN tests, 0 unexpected; 신규 tests/test-agent-denote-signature.el 포함; baseline 96/96 실측 20:13:44" (시민 회신 20:14, 재현·원인 denote.el:4883 확정)

## tick log

### tick 1 — 2026-09-07T18:31 KST

```
state    : advanced
claim    : 미분류 이슈 79개 중 5개(sorge#5,sorge#4,sorge#1,agent-config#23,doomemacs-config#11)를 골라 분류하고 TRIAGE.md 형식을 새로 세웠다
receipt  : gh search issues --owner junghan0611 --state open --limit 100 → 79건 (repo#번호,title 목록 확보)
           gh issue view <n> --repo <repo> --json author,title,body,labels,createdAt → 5건 본문 확인 (author=junghan0611 계정, 각 본문 첫 줄이 실제 작성 에이전트를 별도 명시)
           gh issue view 11 --repo junghan0611/doomemacs-config --json state,comments → state=OPEN, comments=0 (닫혀있지 않음 확인)
deferred : 나머지 74개는 다음 tick으로. 우선순위 기준 없음 — 최신 updatedAt 순서로 상위 5개를 그대로 집었다(임의, 다음 tick에서 기준을 정할지는 GLG 결정)
unexplained : 없음
scope    : TRIAGE.md 신설만. 이슈 본문·코드·다른 파일 손대지 않음
boundary : 없음 — LOOP.md/LEDGER.md/AGENTS.md/NEXT.md/run.sh 미접촉
decisions: (1) sorge#1 — 3집 권한계약 확정을 GLG가 결정해야 진행됨 (2) agent-config#23 — house=미배정인 채로 이 루프의 자기지시적 설계 이슈를 계속 트리아지 대상에 둘지 GLG가 정해야 함 (3) trust 축 — GitHub author는 전부 junghan0611 계정이지만 본문 첫 줄이 "Author: <agent> — not GLG direct"를 매번 명시한다. 지금은 "GLG계정"으로 적었는데 이게 LOOP.md의 trust=GLG본인/형제/외부 셋 중 어디인지 축 자체가 애매하다 — 형제 세션 답신에서 이 축 문제를 따로 짚었다
next     : 다음 tick에서 나머지 74개 중 5개 더. 우선순위 기준(최신순 유지 vs house별 순회 vs LEDGER 배정 리포 우선)을 GLG가 정하면 반영
cost     : turns=1, tokens=(세션 누계, 개별 tick 계측 안 함)
```

### tick 1b — 2026-09-07T19:50 KST — 계약 변경 반영 (GLG 직접 지시, 루프 밖)

```
state    : advanced
claim    : GLG가 게이트를 뒤집었다 — 부르는 것은 sorge, 미는 것은 GLG. LOOP.md·AGENTS.md 를 GLG 지시로 고쳤고(루프 tick 이 아니라 GLG 동석 세션) 5줄을 ball·state 축으로 재분류했다
receipt  : LOOP.md — mission 재작성 · done_when 둘째 줄 · scope allow 확장 · never 개정 · § 착수 § 모델 § 기록 신설 · ball/state 축 · 착수 조건 · tick 지침 3단계 · verdict 에 team/proposal
           AGENTS.md — 「자동 발신 금지」→「sorge 이름으로 남의 집에 앉는 것 금지」 · 경계 표 2줄 · 오독 1줄
           mkdir ~/repos/wt → 비어 있음 (ls 실측)
           house 정정 2건: sorge#5 sorge→doomemacs-config (일이 일어나는 집) · sorge#4 sorge→garden(미배정)
deferred : 첫 워크트리 착수. 조건 충족 1건(doomemacs-config#11) — GLG 가 "일단 하고 나서 검수" 라 했으니 계약 검수 뒤 다음 tick 에서
unexplained : 없음
scope    : LOOP.md · AGENTS.md (guarded — GLG 동석 하에) · TRIAGE.md · ~/repos/wt/ 생성
team     : 없음 (이 tick 에 앉힌 형제 없음)
boundary : 변했다 — 착수 게이트가 GLG 건별 승인 → 다섯 축 부류 승인. AGENTS.md 에 이전 문장과 뒤집은 날짜를 남겼다
decisions: (1) 착수 조건 통과한 doomemacs-config#11 을 다음 tick 에 첫 워크트리로 팔지 (2) sorge#4 — garden 을 LEDGER 에 올릴지 (3) 이슈가 sorge 에 걸리고 일은 남의 집인 패턴이 sorge#1~6 전부다 — house 정의를 「일이 일어나는 집」으로 TRIAGE.md 머리에 박았는데 LOOP.md 축 표에도 올릴지
proposal : 없음 (아직 state=제안 없음)
next     : GLG 계약 검수 → 통과하면 tick 2: 분류 5 + doomemacs-config#11 착수
cost     : turns=1 (GLG 동석)
```

### tick 1c — 2026-09-07T20:12 KST — sol 검수 반영 + 첫 워크트리 pilot (GLG 동석, 루프 밖)

```
state    : advanced
claim    : sol(gpt-5.6-sol) 이 계약을 적대적으로 읽어 다섯 파손을 짚었고 GLG "가자" 로 전부 반영했다. 첫 attempt 를 열었다 — WIP=1
receipt  : sol 답신 20:03 KST (메일함 2026-09-07T11-03-24-255Z-7e9520) — A 깨어남 / B 파손 5 / C 결정 3 / D 못 박을 문장
           [확인] entwurf_resume_call 계약: "Only pi citizens have a same-id resume" → Opus 시민은 죽으면 새 gid
           [확인] LEDGER.md:61 판정 칸 `배정` vs 근거 "후보 제안" 충돌 → GLG 확정으로 교체
           git -C ~/repos/gh/doomemacs-config worktree add ~/repos/wt/doomemacs-config/11 -b attempt/11 → "HEAD is now at 47293e7"
           entwurf_fresh_call claude-code/opus cwd=~/repos/wt/doomemacs-config/11 → window @185, nonce mux-fresh-call-799899d1…
           콜백 20:11:39 KST → impl gid 20260907T201133-7972a1
           담당자 문서 실재: ~/sync/org/botlog/20260227T120800--§doomemacs-config-담당자-….org (denotecli read OK)
deferred : 시민의 done_when 회신 → 오면 이 줄 done_when= 채움. 검수 형제 호출은 ready-for-review 뒤
unexplained : 없음
scope    : LOOP.md(watch join · cadence WIP=1 · never 2줄 · § 착수 재작성 · 축 표 · 격자 · tick 지침 · § driver 신설) · AGENTS.md § 대상 1문장 · LEDGER.md:61 · TRIAGE.md · ~/repos/wt/doomemacs-config/11 생성
team     : sol 20260907T195719-378d7e@openai-codex/gpt-5.6-sol 검수(계약) 19:57 착석 → 20:03 회신 → 물러남(창은 열려 있음)
           impl 20260907T201133-7972a1@claude-code/opus 구현(#11) 20:11 착석 → 진행 중
boundary : 변했다 — 게이트가 부류 승인(격자 8항)으로 확정. driver 의 허용 범위가 문장으로 고정됨
decisions: (1) 물러난 시민의 tmux 창 정리 — verb 없음, GLG 눈으로. 쌓이면 entwurf 이슈 (2) 검수 학교 — sol 다시 부를지 다른 학교(terra/glm/grok)로 갈지
proposal : 없음
next     : impl 회신 대기. done_when 오면 박고, ready-for-review 오면 검수 형제 착석
cost     : turns=1 (GLG 동석) · sol 1턴 · impl 진행 중
```

### tick 1d — 2026-09-07T20:27 KST — 첫 attempt 한 바퀴: 착수 → 구현 → 검수(defect) (GLG 동석)

```
state    : escalate
claim    : #11 attempt 가 착수→done_when→구현→ready-for-review→검수 를 16분에 돌았다. 검수 verdict=defect 2건이고 둘 다 코드 오류가 아니라 GLG 판단 사항이라 여기서 멈춘다
receipt  : impl 20:14 done_when 회신 → 20:20 ready-for-review, commit 2d53238, 3파일 +304/-3 [sorge 대조: git log main..attempt/11 → 2d53238 하나, diff --stat 일치, status clean]
           review 20:21 착석 → 20:26 verdict=defect. [측정 review] "Ran 102 tests, 102 results as expected, 0 unexpected (2026-09-07 20:22:12+0900)"
           [측정 review] 강제 error 후 cl-letf 대상 함수값 = original (비지역 탈출 복원 OK)
           [측정 review] FM 에 `#+signature:` 줄이 있되 빈 값 → 결과 ==oldsig 유지 + 본문 `#+signature:  oldsig` 로 바뀜 (docstring 약속과 어긋남)
deferred : 수정 2차 — GLG 가 아래 둘을 정하면 새 gid 가 같은 워크트리에서 받는다 (impl 은 물러났고 resume 불가)
unexplained : 없음
scope    : TRIAGE.md 만. 워크트리는 시민 것
team     : impl 20260907T201133-7972a1@claude-code/opus 20:11 착석 → 20:20 ready-for-review 회신 → 물러남 (창 3 열림)
           review 20260907T202141-ce4a0c@openai-codex/gpt-5.6-sol 20:21 착석 → 20:26 defect 회신 → 물러남 (창 4 열림)
boundary : 변하지 않았다. 검수가 권한 경계 확대(rename→content write)를 잡아낸 것이 이번 바퀴의 값
decisions: (1) `#+signature:` 가 있되 빈 값 = 의도적 삭제인가 placeholder 인가 (2) rename 권한(파일명만) 아래서 본문에 `#+signature:` 줄을 쓰는 것을 허용할 것인가 — 허용하면 agent-server.el:274-283 계약 문장을 바꿔야 하고, 불허하면 fallback 을 접고 bulk 처럼 skip+WARN 으로 가야 한다
proposal : 없음 — defect 라 제안 불가
next     : GLG 결정 → 새 gid 착석(2차) → 재검수 → 제안. WIP 는 여전히 1 (이 attempt 가 열려 있음)
cost     : impl 1턴(9분) · review 1턴(5분) · sorge 동석
```
