# Workspace 발신함 — 합의와 검증 경계

2026-10-23. 논의: pi-durable 코디 `20261019T114329-71785c`와 Claude Code Opus `20261019T123505-bfabac`. 실행 계약은 **`.claude/skills/sorge/SKILL.md` §inbox 하나**다. 이 문서는 설계 경위와 증거이며 별도 실행기를 정의하지 않는다.

## 목적과 현재 승인

GLG의 직접 지시(현재 코디 대화): 힣봇·힣닷의 발견을 GLG가 매번 읽고 다른 집으로 중계하지 않아도 누군가 접수·검토·응답해야 한다. 작은 범위부터 시작하며 지금 옆의 Opus가 당분간 대응한다. 별도 Sonnet은 구조가 안착한 뒤 고려한다.

10/23 최종 지시: **원문 답변 허용. 정리·커밋·푸시 후 루프 시작.** Entwurf 코디 메시지는 추후 확장이며 지금 허용하지 않았다. 최초 시험은 private `workspace-glgdot`에서 했으며 GLG의 후속 지시로 `workspace-bbot`·`workspace-mini`도 열었다. 허용 집의 실물 목록·ID는 스킬 한 곳에 둔다. 공개 이슈 전체 순회·허용 표 밖 workspace·수선·PR·닫기·새 형제 호출은 이번 승인이 아니다. #30 Cloudflare 실험 및 #28의 stock RobOMP 격리 문제와 별도다.

## 선택 — 실행기 대신 스킬과 기존 루프

- 기존 Opus 세션이 `/sorge inbox` 업무를 수행한다. 사람에게 URL을 요구하지 않고 목록에서 미응답 한 건을 찾는다.
- 같은 세션의 self-paced `/loop`가 정상 틱 뒤 3600초 wakeup을 예약한다. 스킬이 재예약이나 scheduler를 구현하지 않는다.
- 원문에 실질 검토·근거·다음 손·질문을 남기며 단순 접수확인으로 끝내지 않는다. 첫 검토 답변 마커로 다음 호출이 처리 여부를 재확인한다.
- GLG 결정이 필요하거나 대응이 막힌 사건만 DM한다. 빈 틱·진행 중계는 알리지 않는다.
- LOOP의 기존 조용한 시간(23:00–08:00 KST)은 지킨다. 별도 서비스·timer·코드·신규 패키지 없음.

## 관측과 미실증

**코디 GitHub GET receipt, oracle 10/19:** `pass` 봇 PAT 복호화 성공, `/user` login `sorge-bot` / numeric ID `329314842`. GLG의 권한 확대·초대 수락 뒤 scopes에 `repo` 반영, 만료 2026-12-30 15:00 UTC. 발신함 ID `1418425285`, private, pull/push/triage true, admin false. issue GET 200. 접근 가능한 모든 workspace를 자동 접수하지 않았다. 10/23 GLG의 bbot·mini 참여 지시 후 코디가 세 집의 repo ID·private 메타데이터를 재조회했다. 비밀값은 출력하지 않았다.

**10/23 수동 검증:** 코디와 Opus 각각 repo/private·작성자 ID `31724164`·제목 `[sorge]`·open·PR 제외·댓글 pagination/완료 마커를 확인했다. URL 없는 목록 명령으로 첫 요청을 찾았다. Opus가 초안을 작성하고 코디가 공개 근거를 독립 대조했다. 비공개 payload는 공개 문서에 복사하지 않는다. 이 단계는 원문 게시나 예약 성공의 증거가 아니다.

**Opus 자기 도구 스키마 관측, 10/23:** 살아 있는 프로세스는 Claude Code 2.1.303, `ScheduleWakeup` 존재, `CronCreate/List/Delete` 검색 결과 없음. 코디의 PATH CLI는 2.1.309 — 설치 버전과 살아 있는 프로세스 버전은 다르다. 현재 확실한 것은 self-paced 경로이며 고정 cron 가용성을 추정하지 않는다.

**공식 문서 read, 10/23:** https://code.claude.com/docs/en/scheduled-tasks — 같은 세션의 문맥·도구·권한 승계, idle 때 실행, missed tick을 횟수대로 몰아 실행하지 않음, self-paced는 재개 시 복원 안 됨, 7일 만료. 고정 CronCreate 작업의 재개 복원과 섞지 않는다. 이 수명·busy·만료 조건은 로컬 실증 전이며 시작 영수증은 별도 확인한다.

## 논의에서 바로잡은 것

- 10/19의 systemd 폴러 + 도구 0 모델 턴은 미채택 대안이다. GLG가 기존 보이는 하네스를 선호해 별도 실행기를 만들지 않기로 좁혔다.
- pi heartbeat의 1순위 추천도 철회했다. Opus가 `agent-config/pi-extensions/heartbeat.ts:193-205`를 읽어 기억축 조회·기록 등 고정 틀이 이번 발신함 점검과 맞지 않는다고 확인했다(코디에겐 상속된 판독).
- private/작성자 gate·프롬프트 지침은 프로세스 격리가 아니다. Opus 측 10/23 관측에서 OpenClaw 컨테이너의 gh 인증은 `junghan0611`/`31724164`였으므로 author gate는 그 토큰을 가진 GLG·형제를 구분하지 않는다. bbot의 외부 입력 허용 범위는 이번 작업에서 확인하지 않았고, 입력을 데이터로 다루는 경계가 필요하다. 기존 Opus는 같은 uid·풀도구/권한 확인 생략 모드이며, GLG의 보이는 세션 운영 선택으로 범위를 제한한다. #28 해결을 주장하지 않는다.
- 접수된 요청은 수선/전달 권한을 만들지 않는다. 게시 토큰 identity를 확인하고 실패 시 기본 GLG gh 인증으로 fallback하지 않는다.
- 봇 댓글 아무거나가 아니라 봇 numeric ID + 첫 검토 마커로 완료를 판정한다. 후속 대화·본문 수정 자동 재처리는 v1 범위 밖이다.
- POST 결과 유실에는 자동 재게시하지 않는다. 단일 운영자·재조회로 범위를 줄일 뿐 exactly-once를 보장하지 않는다.
- 운영 상태의 필요성을 LEDGER 규율로 금지하지 않는다. 현재는 GitHub 원문의 완료 마커로 다시 유도하며 새 상태 저장기는 만들지 않는다.

## 원문 좌표

- https://github.com/junghan0611/sorge/issues/31 — 발신함 제안과 경계
- https://github.com/junghan0611/sorge/issues/28 — 기존 stock 격리 사고, 여전히 별도 미해결
- `.claude/skills/sorge/SKILL.md` — 업무·조회·원문 응답 계약
- `LOOP.md` §mission / `AGENTS.md` §봇이 남길 때 — 손의 권한과 저자 표시

첫 가동 뒤 실제 댓글 URL·봇 신원·완료 제외·다음 wakeup 영수증은 NEXT의 현재 상태에 반영한다. 예약 접수는 다음 틱 실행 증거가 아니다.
