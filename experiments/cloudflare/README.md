# Cloudflare 실험 — 코드의 한 시점

독립된 형제들이 같은 코드의 출발점을 읽는 작은 Worker. 완성된 협업 시스템이 아니다.

## 지금 되는 것

- `/` — commit SHA를 넣어 읽는 화면.
- `/api/snapshot?commit=<40자리 SHA>` — 설정된 저장소의 commit, 그 시점의 `README.md`·`AGENTS.md`.
- 모든 파일은 같은 SHA에서 읽는다. 움직이는 branch를 검토의 기준으로 쓰지 않는다.
- 읽기만 한다. 저장소 생성·토큰 발급·push·이벤트 구독·형제 호출·자동 머지 없음.
- 저장소명은 서버 설정에만 둔다. 화면은 저장소 내용도 명령이 아니라 텍스트로 표시한다.

## 로컬에서 만져보기

리포 루트에서:

```sh
node --test experiments/cloudflare/worker.test.mjs
node experiments/cloudflare/local.mjs
# 다른 터미널에서 현재 commit 확인:
git rev-parse HEAD
```

`http://127.0.0.1:8787`에서 SHA를 넣는다. `/?commit=<SHA>` 링크로 같은 시점을 공유할 수도 있다.

**로컬 미리보기는 실제 로컬 Git을 읽지만 Cloudflare 연결은 아니다.** `local.mjs`의 adapter는
preview용이며, Artifacts 응답 타입·인증·서비스 동작을 검증하지 않는다. 결과에 `local-git-preview`를 표시한다.
UI는 현재 작업 트리가 아니라 선택한 커밋의 파일을 읽는다.

## Cloudflare로 넘어갈 때

`wrangler.jsonc`의 namespace `sorge-experiment`, repo `code-snapshot`은 아직 생성하지 않은 예시다.
**공개해도 되는 실험 데이터만** 넣는다. 현재 HTTP 화면에는 사용자 인증이 없으므로 개인 저장소용이 아니다.
**현재 후보는 공개 배포하지 않는다.** 공개 읽기 요청도 과금 백엔드를 반복 호출할 수 있다.
실제 Artifacts 연결 전에 인증·요청량 상한을 정하고, 미인증 요청이 binding에 닿지 않는 테스트를 추가한다.

1. Workers Paid와 Artifacts 사용 권한을 확인한다. 구독·결제는 GLG 결정.
2. 실험 namespace/repo와 초기 commit을 준비하고 설정을 맞춘다. Artifacts repo는 변경 운반체이지 새 관리 대상 리포가 아니다.
3. 공식 문서가 요구하는 Wrangler **4.145.0 이상**을 마련한다. 전역 도구 버전 관리는 nixos-config 담당자 몫.
4. `cloudflare` 스킬의 토큰 경로와 dry-run → 확인 → 실행 순서를 따른다.
5. 실제 Artifacts에서 같은 SHA를 읽어 Git 결과와 대조한다. 로컬 테스트 통과로 이 단계를 대신하지 않는다.

2026-10-07 이 호스트 측정: Wrangler **4.143.0**의 `deploy --dry-run --outdir dist --autoconfig=false`는
Artifacts binding을 인식하고 번들을 만들었다. **배포·계정 요금제 확인·실제 Artifacts 읽기는 하지 않았다.**
공식 문서는 remote binding의 Blob 반환과 타입 생성을 위해 4.145.0 이상을 요구한다.
설치된 Wrangler `wrangler-dist/cli.js:26571–26665` 판독: Artifacts는 로컬 simulator가 없고,
`wrangler dev`에서도 원격 자원에 접근한다. 따라서 이를 결제 전 오프라인 시험으로 사용하지 않는다.
Workers 자체는 Free plan으로 실행할 수 있으나, 그것은 Artifacts 실증과 별개다.

## 다음 실험 — 아직 실행하지 않음

실제 Artifacts 읽기가 되면 서로 다른 형제가 이 작은 프로그램을 함께 바꾼다.
예를 들어 한 형제는 두 후보 비교를, 다른 형제는 ‘검토한 SHA와 현재 SHA가 달라졌음’ 표시를 만든다.
겹치는 변경과 검토 결과를 보고 필요한 접점을 찾는다. 작업 배정·스키마·참여 스킬은 그때 정한다.
지금의 읽기 화면만으로 동시 변경·충돌·검토·선택 문제를 해결했다고 보지 않는다.

## 근거

- 논의: https://github.com/junghan0611/entwurf/issues/131
- 문제: https://blog.cloudflare.com/next-git-platform-on-cloudflare/
- binding: https://developers.cloudflare.com/artifacts/api/workers-binding/
- events: https://developers.cloudflare.com/artifacts/guides/event-subscriptions/

공식 binding 문서 판독에 따라 `get`·`readCommit`·`readFile`·disposable capability를 사용했다.
Node 테스트는 대역으로 경계와 실패 처리를 확인하고, HTTP 테스트 한 건은 실제 로컬 Git을 읽는다.
