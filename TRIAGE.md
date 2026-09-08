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
junghan0611/prime-agent#2	house=prime-agent(배정, 20260521T134542) kind=운영 authority=읽기 reversible=예 money=아니오 trust=형제(claude-opus-5, 본문 첫 줄 서명) deadline=없음 ball=GLG verdict=GLG결정필요(본문 자체가 결정 시트 — A 8건 + J1 terminal status 집합 승인. 「도출이 아니라 승인/기각」이라 에이전트가 대신 정할 수 없다) state=분류
junghan0611/prime-agent#1	house=prime-agent(배정, 20260521T134542) kind=기능 authority=쓰기 reversible=예 money=아니오 trust=형제(grok-4.6 본문 서명, 배너·스레드는 후속 형제) deadline=없음 ball=GLG verdict=보류(prime-agent#2 결정 10건 선행 — 본문 배너가 CURRENT=H1–H8 재감사라 명시. 게다가 자체 조율 레인이 이미 돈다: coordinator=claude-fable-5-1) state=분류 곁=본문이 「스레드가 이긴다」고 스스로 선언한다(댓글 36개). 마지막 회신 2026-09-02 는 H12 를 feat/clojure-runtime @bc4a68ba 위 **워킹트리 미커밋**으로 보고 [출처: 이슈 스레드, sorge 미검증]
junghan0611/doomemacs-config#8	house=doomemacs-config(배정, 20260227T120800) kind=기능 authority=발행(upstream 이슈화가 산출물 — 「K 검수 산출물」) reversible=아니오(neomacs 바이너리 부팅·한글 IME·org 표 정렬 실동작 검증이 워크트리 밖) money=아니오 trust=GLG본인(에이전트 서명 없음) deadline=있음(「한 달 이내」, 2026-06-15 기준 이미 경과) ball=담당자 verdict=GLG결정필요(착수 격자 3항 위반: authority>쓰기 · reversible=아니오 · deadline 있음) state=분류 곁=sorge#5 가 이 이슈의 3집 분배(doomemacs-config·추적노트 20260209T123532·nixos-config)를 들고 이 집은 「측정」 몫만 소유한다(그 집 마지막 댓글 2026-09-06)
junghan0611/doomemacs-config#10	house=doomemacs-config(배정, 20260227T120800 — 수정은 upstream ghostel 이 아니라 이 집 lisp/term-config.el 의 advice 다: 본문 「harden in our layer, don't patch the straight package」) kind=버그 authority=쓰기 reversible=예(advice 한 개, 워크트리 안에서 닫힘) money=아니오 trust=GLG본인(에이전트 서명 없음) deadline=없음 ball=담당자 verdict=보류(본문이 스스로 「Low priority; tracking only (not on NEXT)」로 닫아뒀다 — 조건: 에코 영역 노이즈 빈도가 오르면 준비된 advice 적용) state=분류 곁=원인·수정본·트레이드오프가 본문에 이미 다 있다(C-g 가 native redraw 콜백 창에 떨어져 env 의 non-local-exit 를 오염 → 다음 copy_string_contents 가 ExtractStringFailed 로 오표시). **착수 격자는 전부 통과하지만 담당자가 의도적으로 미뤘으므로 루프가 뒤집지 않는다**
junghan0611/sicm-study#2	house=sicm-study(배정, 20260303T195201) kind=씨앗 authority=읽기 reversible=예 money=아니오 trust=GLG본인(1인칭 독서 기록 — 「나는 AI 연구자가 아니고」) deadline=없음 ball=담당자 verdict=담당자몫 state=분류 곁=착수 격자를 유일하게 전부 통과한다(막는 것은 살아있는 attempt=1 뿐). 다만 authority=읽기 인 탐구 앵커라 **워크트리 안에서 닫히는 done_when 이 도출될지가 관문**이다 — 산출물이 ~/org 로 나가면 never 규칙에 걸려 GLG결정필요로 내려간다. 마지막 댓글(2026-08-30, GPT-5.6 Sol)이 sicm-study#2·entwurf#88·prime-agent#1 을 「공존의 언어」 한 축으로 묶었다 — 횡단 발견 후보
junghan0611/sorge#13	house=sorge(배정, 20260227T031800) kind=운영 authority=읽기(가리키고 종만 친다 — 설계 판정·남의 리포 커밋 없음) reversible=예 money=아니오 trust=GLG본인(GLG 지시로 개설) deadline=없음 ball=담당자 verdict=담당자몫 state=분류 곁=**이 집 최초의 「크로스 이슈 매니징」 판본이다.** GLG 판정 2026-09-08: *"sorge는 sorge 단독 이슈보다 크로스 이슈를 매니징해야 하니까."* entwurf#109(브랜치 explore/109, 코드 0줄) · nixos-config 세션 레인(20260908T132558-6797cf) 둘을 가리킨다. 트립와이어 넷(새 상주 프로세스 · 주소 권위 안 경로 번역 · 두 번째 신원 축 · 파생 저장소)이 걸리면 이름 붙여 GLG에게 보인다. 착수 격자는 안 본다 — 이 집 몫이고 authority=읽기라 워크트리가 필요 없다
junghan0611/sorge#12	house=nixos-config(**대상 밖 — 대장에 없음**) kind=운영 authority=읽기(1차는 관측·알림·제안까지만, 본문 §4 가 자동 kill/cleanup/restart 를 배제) reversible=예 money=아니오 trust=형제(gpt-5.6-terra 서명, GLG 계정) deadline=없음 ball=담당자 verdict=보류(대상 아님) state=분류 곁=밤 루프 종료(06:15) 뒤 03:04Z 에 난 이슈라 원장에 없었다. **오늘 세 번째로 「대상 밖」이 산 이슈를 덮는다** — 같은 날 entwurf 담당자가 경로 스큐 흡수처를 nixos-config 로 판정했고(entwurf#109 첫 판정), 그 집이 대장에 없다. 본문 실측: PPID=1 인 copilot-receive receiver 362개 · /tmp fixture root 720개 — 중단된 hermetic gate 잔해
junghan0611/junghan0611#4	house=junghan0611(배정, 20260318T183247) kind=기능 authority=발행(ax.junghanacs.com 공개 증거면에 나간다 — 댓글이 Phase 1 을 「배포했다」로 보고) reversible=예(편집은 리포 안 apply/ax/ax.org 한 장, 산출물은 거기서 생성) money=아니오 trust=GLG본인(에이전트 서명 없음 — 본문은 GLG 문제제기 + Opus·GPT 교차검토의 합의문) deadline=없음 ball=담당자 verdict=GLG결정필요(격자 위반 1항: authority>쓰기. 공개 증거면이라 무엇을 싣고 뺄지는 담당자가 먼저 가른다) state=분류 곁=**house 함정** — 본문의 `apply/ax/ax.org` 는 apply 리포가 아니라 이 리포 안의 디렉터리다 [측정: ls ~/repos/gh/junghan0611/apply/ax/ax.org → 78502 bytes, 2026-08-04. ~/repos/gh/apply/ax/ 는 없음]. 경로 첫 마디가 리포 이름과 같아서 apply 로 흘릴 뻔했다

### 보류(대상 아님) — 한 줄로 조용히 닫은 것

아래 줄들이 짧은 것은 미완이 아니라 **판정이 없기 때문**이다. `AGENTS.md § 대상` — 대장에 줄이 없는
리포는 미판정이 아니라 대상 밖이고, 순회는 그것을 *세지도 묻지도 않는다*. 축을 채우려면 본문 65건을
읽어야 하는데 그 독서 자체가 「묻지 않은 곳을 넓히는 일」이다. 그래서 `house` 와 `verdict` 만 든다 —
`done_when` 의 집합 연산이 첫 칼럼만 보기 때문에 이것으로 충분하고, GLG 가 어느 집을 대장에 올리면
그때 그 줄이 다시 뜬다.

`sorge#N` 은 `house` 를 「일이 일어나는 집」으로 풀었다(제목 기준). **entwurf 3건(#10·#9·#8)은 본문을
열지 않았다** — GLG 가 릴리즈 중이라 손대지 말라 했고, 제목만으로 대상 밖이 확정되므로 열 이유가 없다.

junghan0611/GLG-Mono#2	house=GLG-Mono(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/abductcli#1	house=abductcli(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/agent-config#1	house=agent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/agent-config#10	house=agent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/agent-config#13	house=agent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/agent-config#14	house=agent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/agent-config#15	house=agent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/agent-config#16	house=agent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/agent-config#17	house=agent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/agent-config#20	house=agent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/agent-config#21	house=agent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/agent-config#3	house=agent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/agent-config#5	house=agent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/agent-config#6	house=agent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/andenken#12	house=andenken(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/andenken#13	house=andenken(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/andenken#9	house=andenken(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/butlercli#1	house=butlercli(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/butlercli#2	house=butlercli(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/edgeagent-config#1	house=edgeagent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/entwurf#76	house=entwurf(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/entwurf#78	house=entwurf(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/entwurf#88	house=entwurf(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/entwurf#95	house=entwurf(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/entwurf#97	house=entwurf(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/geworfen#2	house=geworfen(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/ghostel#1	house=ghostel(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/homeagent-config#10	house=homeagent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/homeagent-config#2	house=homeagent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/homeagent-config#3	house=homeagent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/homeagent-config#4	house=homeagent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/homeagent-config#5	house=homeagent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/homeagent-config#6	house=homeagent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/homeagent-config#7	house=homeagent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/homeagent-config#8	house=homeagent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/homeagent-config#9	house=homeagent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/jacobian-lens#1	house=jacobian-lens(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/lifetract#1	house=lifetract(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/memex-kb#2	house=memex-kb(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/memex-kb#4	house=memex-kb(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/memex-kb#5	house=memex-kb(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/memex-kb#6	house=memex-kb(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/nixos-config#3	house=nixos-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/nixos-config#5	house=nixos-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/nixos-config#9	house=nixos-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/sks-gateway-v2#1	house=sks-gateway-v2(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/sks-gateway-v2#10	house=sks-gateway-v2(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/sks-gateway-v2#11	house=sks-gateway-v2(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/sks-gateway-v2#12	house=sks-gateway-v2(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/sks-gateway-v2#13	house=sks-gateway-v2(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/sks-gateway-v2#14	house=sks-gateway-v2(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/sks-gateway-v2#15	house=sks-gateway-v2(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/sks-gateway-v2#16	house=sks-gateway-v2(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/sks-gateway-v2#17	house=sks-gateway-v2(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/sks-gateway-v2#2	house=sks-gateway-v2(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/sks-gateway-v2#3	house=sks-gateway-v2(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/sks-gateway-v2#4	house=sks-gateway-v2(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/sks-gateway-v2#5	house=sks-gateway-v2(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/sks-gateway-v2#6	house=sks-gateway-v2(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/sks-gateway-v2#7	house=sks-gateway-v2(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/sks-gateway-v2#8	house=sks-gateway-v2(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/sks-gateway-v2#9	house=sks-gateway-v2(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/sorge#10	house=entwurf verdict=닫아도 됨(이관 → entwurf#108, 2026-09-08) state=폐기 곁=GLG 지시로 entwurf 담당자(20260908T151205-1ac964)가 재측정 댓글 달고 가져갔다. **이 집 몫 끝** — 원본 sorge 이슈는 closed
junghan0611/sorge#2	house=garden(대상 밖 — 대장에 없음, sorge#4 와 같은 집) verdict=보류(대상 아님) state=분류
junghan0611/sorge#3	house=garden(대상 밖 — 대장에 없음, sorge#4 와 같은 집) verdict=보류(대상 아님) state=분류
junghan0611/sorge#6	house=agent-config·entwurf(둘 다 대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/sorge#7	house=agent-config(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/sorge#8	house=entwurf verdict=닫아도 됨(이관 → entwurf#106, 2026-09-08) state=폐기
junghan0611/sorge#9	house=entwurf verdict=닫아도 됨(이관 → entwurf#107, 2026-09-08) state=폐기 곁=**컨테이너 다리는 #9 에 얹지 않고 entwurf#109 로 따로 섰다** — 원인 계열은 같으나(dispatch 가 한 로컬 경로 네임스페이스를 전제한다) 수락조건이 다르다(마운트·MCP scope vs 인증 SSH 레일). 판정자는 entwurf 담당자
junghan0611/tuyahome#1	house=tuyahome(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/tuyahome#3	house=tuyahome(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류
junghan0611/tuyahome#4	house=tuyahome(대상 밖 — 대장에 없음) verdict=보류(대상 아님) state=분류

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

### tick 2 — 2026-09-07T22:52 KST — 밤 루프 첫 tick (worker: claude-code/opus, GLG 부재)

```
state    : advanced
claim    : 대장 배정 리포에 걸린 미분류 5건(prime-agent#2·#1, doomemacs-config#8·#10, sicm-study#2)을 분류했다. 착수·검수는 열리지 않았다 — #11 이 살아 있어 WIP=1 이고, GLG 가 그 defect 2건을 "나중에 볼거야" 로 잡아뒀다
receipt  : TZ='Asia/Seoul' date → 2026-09-07T22:52 KST
           gh search issues --owner junghan0611 --state open --limit 100 → 83건
           comm -23 <(전체) <(TRIAGE 첫 칼럼) → 미분류 73건 (총 83 / 분류 10)
           gh issue view <n> --repo <repo> --json title,author,createdAt,labels,body → 5건 본문 정독
           gh issue view <n> --json comments → 스레드 길이 확인: prime-agent#1=36, prime-agent#2=7, sicm-study#2=5, dc#8=4, dc#10=0
           [정정] dc#10 의 house 는 ghostel 이 아니다 — 본문 「Prepared local fix」 절이 수정 자리를 이 집 lisp/term-config.el 의 define-advice 로 못박는다("harden in our layer, don't patch the straight package"). 제목만 읽었으면 대상 밖으로 흘릴 뻔했다
           git diff --stat LOOP.md → 8 insertions, 5 deletions (미커밋). 낮 세션(GLG 동석)이 opus 전환·첫밤 예외·driver 절을 넣은 것. **worker 는 읽기만 했다**
deferred : ② 착수 0건 — sicm-study#2 가 착수 격자를 전부 통과하지만 「살아있는 attempt=0」 하나에서 막힌다(#11 이 state=검수 로 열려 있음). ③ 검수 0건 — ready-for-review 회신이 온 워크트리 없음(#11 은 이미 검수까지 돌았고 defect 로 GLG 앞에 서 있다)
unexplained : 없음. 79→83 증가 4건은 전부 sorge#7~#10 이고 createdAt 이 10:21:46Z~10:55:20Z(=19:21~19:55 KST)로 tick 1(18:31) 이후다 → external(낮 레인)이지 설명 없는 변화가 아니다
scope    : TRIAGE.md 만 (이슈 5줄 추가 + 이 블록). 워크트리 0개 팜/지움. 이슈 밖 쓰기 0. entwurf 무접촉
team     : 없음 — 이 tick 에 앉히거나 물린 형제 0명
boundary : 변하지 않았다. guarded 5파일 미접촉(LOOP.md 는 diff 확인만 하고 쓰지 않음)
decisions: (1) **분류 우선순위 기준 — 승인/기각 하나.** tick 1 이 열어둔 물음을 오늘 밤은 「대장 배정 리포 우선, 그 안에서 updatedAt 최신순」으로 가정하고 돌았다. 근거는 대상 밖 줄이 정보를 안 낳는다는 것. 아니면 다음 tick 부터 바꾼다
           (2) **tick 당 5개 상한을 대상 밖 줄에도 그대로 걸 것인가.** 실측: 미분류 73건 중 대장 리포에 걸린 것은 8건뿐이고(junghan0611#4 · sorge#2/3/6/7/8/9/10), 그중 7건이 sorge#N 이라 house 는 대개 남의 집이다. 나머지 65건은 sks-gateway-v2 17 · agent-config 12 · homeagent-config 9 · entwurf 5 … 로 전부 「보류(대상 아님)」 한 줄짜리다. 상한 5를 유지하면 정보를 안 낳는 줄을 쓰는 데 13 tick(약 6.5시간)이 든다. 올리려면 LOOP.md 개정이고 그건 guarded — **GLG 의 손이다**
           (3) **doomemacs-config#10 — 담당자가 스스로 미룬 것을 루프가 뒤집지 않는다** 를 확인해달라. 착수 격자는 8항 전부 통과하는데 본문이 "tracking only (not on NEXT)" 로 닫아뒀다. 루프가 격자만 보면 착수 가능으로 읽는다. 이번엔 verdict=보류 로 눌렀지만, 이 우선순위(본문의 담당자 의사 > 격자)를 LOOP.md 에 못박을지는 GLG 몫
           (4) **doomemacs-config#11 defect 2건** — tick 1d 에서 이월. 오늘 밤 손대지 않았다(GLG 지시). 이게 닫혀야 WIP 가 비고 다음 착수가 열린다
           (5) trust 축 — 오늘 밤은 「본문 첫 줄에 에이전트 서명이 있으면 형제, 없으면 GLG본인」으로 조작적으로 갈랐다(prime-agent#1/#2=형제, dc#8/#10·sicm-study#2=GLG본인). tick 1 이 남긴 물음의 잠정 답이니 승인하거나 뒤집어달라
proposal : 없음 — state=제안 인 워크트리 0개
next     : tick 3 — 대장 리포에 걸린 남은 8건 중 5건 분류(junghan0611#4 + sorge#7/#6/#10/#9 순). sorge#N 은 house 를 「일이 일어나는 집」으로 풀어야 하는데 #10/#9/#8 은 entwurf, #7/#6 은 agent-config 로 보인다(제목 기준 예비 판독, 미검증) → 셋 다 대장 밖이면 보류 한 줄. **GLG 요청: entwurf 릴리즈 중이므로 entwurf 는 이슈 본문 읽기조차 하지 않고 제목만으로 대상 밖 처리한다**
cost     : turns=1 (worker 단독)
```

### tick 3 — 2026-09-07T23:26 KST — **done_when 두 조건 다 닫혔다**

```
state    : advanced
claim    : 미분류 73건을 전부 닫아 0 으로 만들었다. LOOP.md § done_when 의 measured 두 줄이 지금 둘 다 참이다 — 이 루프는 「끝난 상태」에 처음 도달했다. 착수·검수는 여전히 안 열린다(#11 이 살아 있어 WIP=1)
receipt  : TZ='Asia/Seoul' date → 2026-09-07T23:26 KST
           [done_when 1] comm -23 <(gh search … | sort) <(TRIAGE 첫 칼럼 | sort -u) → **0줄**. 총 83 / 분류 83 / 미분류 0
           [done_when 2] state=검수 줄 1개(doomemacs-config#11)의 wt=~/repos/wt/doomemacs-config/11 → 디렉터리 실재
             git -C ~/repos/gh/doomemacs-config worktree list → "/home/junghan/repos/wt/doomemacs-config/11  2d53238 [attempt/11]"
           grep … | sort | uniq -d | wc -l → 0 (중복 줄 없음)
           [정정] 첫 comm 이 "미분류 74" 를 냈고 이미 분류된 sorge#1 이 그 안에 들어 있었다. 원인은 로케일 — ko_KR 정렬로 만든 파일에 comm 이 "not in sorted order" 경고를 냈다. LC_ALL=C 로 다시 재서 73 을 얻었다. **집합 연산이 조용히 틀릴 뻔했고, 틀린 쪽은 「덜 분류됨」이 아니라 「이미 한 것을 또 하기」였다**
           [측정] junghan0611#4 의 house 함정: ls ~/repos/gh/junghan0611/apply/ax/ax.org → 78502 bytes(2026-08-04). ls ~/repos/gh/apply/ax/ → No such file. 본문 경로 `apply/ax/ax.org` 의 첫 마디가 대장에 있는 다른 리포 이름과 같다
deferred : ② 착수 0 — 살아있는 attempt=1(#11 state=검수). ③ 검수 0 — ready-for-review 회신 온 워크트리 없음. 둘 다 #11 의 defect 2건이 GLG 손에서 닫혀야 열린다
unexplained : 없음. 83건 그대로(tick 2 이후 신규 0)
scope    : TRIAGE.md 만 — 이슈 73줄 + 「보류(대상 아님)」 절 머리글 + 이 블록. 워크트리 판/지운 것 0. 이슈 밖 쓰기 0. entwurf 본문 열람 0
team     : 없음
boundary : 변하지 않았다. guarded 5파일 미접촉 — LOOP.md 는 § cadence 개정(낮 세션 손, 22:56)을 읽기만 했고 이번 tick 이 그 개정의 첫 적용이다
decisions: (1) **루프를 계속 돌릴 것인가.** done_when 이 닫혔으므로 다음 tick 부터는 새 이슈가 생기지 않는 한 전부 state=noop 이다. 30분마다 깨어나 「변화 없음」을 확인하는 값이 있는지 GLG 가 정한다 — 계속 두면 새 이슈 감지기 역할은 하고, 끄면 tick 비용이 0 이 된다
           (2) **doomemacs-config#11 defect 2건** — tick 1d 이월, 사흘째 같은 자리. ①`#+signature:` 빈 값의 의미(삭제 vs placeholder) ②rename 권한 아래서 본문에 `#+signature:` 줄을 쓰는 것 허용 여부. **이게 닫혀야 WIP 가 비고 sicm-study#2 착수가 열린다** — 지금 유일하게 격자 8항을 전부 통과한 이슈다
           (3) 우선순위 가정(대장 리포 우선·updatedAt 최신순)은 이제 소진됐다 — 분류할 게 없어서다. 승인/기각이 아직 필요한지 자체가 사라졌으니 접어도 된다
           (4) **대장 밖 65건을 한 줄로 닫은 것이 옳은가.** 「세지도 묻지도 않는다」의 문자 그대로 실행이다. 만약 GLG 가 그중 어느 집(예: entwurf 5건, agent-config 12건, andenken 3건)을 대장에 올리면 그 줄들이 즉시 다시 뜬다 — 지우지 않고 남겨뒀기 때문에 재분류 비용이 grep 한 번이다
proposal : 없음 — state=제안 인 워크트리 0개. **제안이 0인 이유는 실패가 아니라 게이트다**: 유일한 attempt 가 검수에서 defect 를 받았고 그 둘이 코드 오류가 아니라 GLG 판단이라 여기서 멈춰 있다
next     : 새 이슈가 생기지 않는 한 tick 4 부터 noop. 시계는 계속 돈다(30분). #11 결정이 내려오면 그 tick 에서 새 gid 를 같은 워크트리에 앉히고 → 재검수 → state=제안 으로 올린다
cost     : turns=1 (worker 단독)
```

### tick 4~15 — 2026-09-08T00:02 ~ 05:41 KST · **12블록 접음**

```
state    : noop × 12 (연속). 원문 12블록이 자간 한 글자 없이 같았다
claim    : 변화 없음. tick 3(23:26)에 done_when 두 조건이 충족된 뒤 외부 사건 0
receipt  : 12블록 전부 동일 — 83/83/미분류 0/닫힌것 0 · wt 11 = 2d53238 clean ·
           guarded mtime 불변 · mail 0
deferred : ②③ — #11 defect 2건이 GLG 손 (12 tick 내내)
unexplained : 없음   scope : 이 블록만   team : 없음   boundary : 불변   proposal : 없음
decisions: tick 3 의 (1)(2) 그대로. tick 15 가 그 자체를 판독했다 —
           "밤새 측정된 것: 22:52~05:41 사이 새 이슈 0, 닫힌 이슈 0, 시민 회신 0.
            감지기로서의 이 루프가 잡은 사건은 0건이었다"
cost     : 12 tick, 각 turns=1
```

> **왜 접었나 (2026-09-08, GLG: *"쌓였으면 덜어내고"*).** tick log 는 append-only 이력이고 그 규율은
> **이미 쓴 것을 고쳐 쓰지 않는다**는 뜻이지 **닫힌 무변화 구간을 원문 그대로 이고 간다**는 뜻이 아니다.
> 12블록이 글자까지 같았고, 밤 전체의 결산은 아래 「루프 종료」 블록과 `CHANGELOG.md v2026.9.8` 이
> 이미 든다. **접힌 것은 반복이지 사실이 아니다** — 위 블록이 12회라는 사실과 그 receipt 를 그대로 든다.
> 자간까지 같았다는 것 자체가 그 밤의 판독이다.

### tick 16 — 2026-09-08T06:12 KST

```
state    : noop
claim    : 변화 없음 (noop 13연속: tick 4~16). GLG 가 06:0x 에 깨어 밤 결산을 물었고 낮 세션(fable)에 결산을 보냈다 — 루프 밖 행위라 여기엔 사실만 적는다
receipt  : 83/83/미분류 0/닫힌것 0 · wt 11 = 2d53238 clean · guarded mtime 불변 · mail 0
           entwurf_v2 → 낮 세션 20260907T182625-62102b, 메일함 2026-09-07T21-11-52-405Z-0081b7.msg (밤 결산 1통)
deferred : ②③ — #11 defect 2건이 GLG 손
unexplained : 없음   scope : 이 블록만   team : 없음   boundary : 불변   proposal : 없음
decisions: tick 3 의 (1)(2). **GLG 가 깨어 있으니 지금 닫을 수 있다** — (1) 루프 지속 여부(밤새 감지 0건이 실측) (2) #11 defect 2건
           (3) 새로 하나: **done_when 의 집합 연산에 LC_ALL=C 를 못박을지.** tick 3 에서 ko_KR 정렬 때문에 comm 이 조용히 틀린 답(74, 이미 분류된 sorge#1 포함)을 냈다. LOOP.md 는 guarded 라 worker 가 못 고친다
next     : GLG 판정 대기. 판정 없으면 30분 noop 유지
cost     : turns=1
```

### 루프 종료 — 2026-09-08T06:15 KST (GLG: "그만 멈춰")

```
state    : advanced
claim    : 밤 루프를 GLG 지시로 껐다. tick 2~16, 15 tick, 22:52~06:12 KST
receipt  : ScheduleWakeup(stop) → "cancelled 1 pending wakeup(s); no further dynamic-loop wakeups scheduled"
           Monitor 는 애초에 안 걸었으므로 정리할 것 없음
결산     : 미분류 73 → 0 (총 83건 전부 원장에). done_when 두 조건 tick 3(23:26)에 충족, 이후 13 tick noop
           착수 0 · 검수 0 · 제안 0 — #11 이 WIP 를 잡고 있었고 그 defect 2건은 GLG 몫이라 손대지 않았다
           커밋 0 · 푸시 0 · 이슈 밖 쓰기 0 · 형제 호출 0 · 워크트리 판/지운 것 0 · entwurf 무접촉
scope    : TRIAGE.md 만 (밤 내내)
team     : 없음 — 이 밤에 앉힌 형제 0명
boundary : 변하지 않았다. guarded 5파일 미접촉
decisions: **셋 다 열린 채로 GLG 에게 넘긴다**
           (1) 루프를 다시 켤 것인가 — 밤새 감지 건수 0 이 그 값의 실측이다
           (2) doomemacs-config#11 defect 2건 (tick 1d 이월) — 닫히면 WIP 가 비고 sicm-study#2 착수가 열린다
           (3) done_when 의 집합 연산에 LC_ALL=C 를 못박을지 — tick 3 에서 실제로 틀린 답을 냈다 (LOOP.md 는 guarded)
next     : 없음. 시계가 꺼졌으므로 다음 tick 은 GLG 가 다시 켤 때 온다
cost     : 15 tick, 각 1턴
```
