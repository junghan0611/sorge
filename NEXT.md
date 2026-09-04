# NEXT — sorge

> 다음 한 걸음. 중기 축은 아직 없다 — 그릇이라 모양이 자라는 중이다.

# RAIL

> 1~8 은 닫혔고 `CHANGELOG.md` `v2026.9.4` 로 갔다 — 집·계약·대장·첫 순회·이슈판 기반.

- [ ] **9. forge + Datasette** ← CURRENT: 이슈판을 실제로 세운다
- [ ] **10. Forgejo 축** — `forge.junghanacs.com` open 11건. 이 캐시엔 구조적으로 안 들어온다

# NOW

- **Next — RAIL 9: 이슈판을 실제로 세운다.** 기반은 `v2026.9.4` 로 닫혔다. 남은 것 둘:
  - **상시로 띄울지 정한다.** 지금은 `./run.sh board` 로 띄우고 세션과 함께 죽는다.
    systemd 로 올릴지, `forge-pull` 뒤에만 볼지는 `doomemacs-config`(DB 주인)와 정할 자리다.
  - **Forgejo 축을 붙인다** (RAIL 10). `forge.junghanacs.com` open 11건은 이 캐시에
    **구조적으로** 안 들어온다 — REST 로 따로 든다.
- **지금 서 있는 것:** `./run.sh board` → http://127.0.0.1:8071 · 렌즈 넷
  (`cross_repo` 25건 · `board` 57 · `by_repo` · `stale_open`).
  `agent-config#3` 하나가 네 리포를 건다 — 그게 이 판을 만든 이유다.
- **`entwurf` 만 배선이 남았다.** GLG가 뺐다(오라클 릴리즈 중, 2026-09-04).
  릴리즈가 끝나면 `printf '@AGENTS.md\n' > CLAUDE.md` 한 줄이면 된다.
- **`junghan0611` 담당자 문서에 README 사본이 아직 있고 diff 가 137줄로 벌어졌다.**
  그 집이 「동기화하지 않는다」를 판정으로 박았으니 결함은 아니다. 다만 **사본 블록을
  걷어내고 리포를 가리키기만 하는 게 낫지 않은가**는 그 집에 리드로 건넬 자리다.

## 이슈판 실측 (2026-09-04, thinkpad) — GLG의 전제가 측정으로 섰다

- forge DB `~/doomemacs/.local/etc/forge/forge-database.sqlite` — 20 repos ·
  **open 57 중 25개(44%)가 본문·제목에서 다른 리포를 이름으로 부른다.** SQL 한 방, 네트워크 0.
  **처음에 60%라고 보고했는데 틀렸다** — 하드코딩한 이름 목록에 `openclaw` 가 섞여 있었고 그건
  DB의 리포가 아니라 소프트웨어 이름이다. `doomemacs-config` 담당자가 재현 실패로 잡아냈고,
  DB의 실제 `repository.name` 만 써서 다시 재니 그의 수치와 정확히 일치했다(2026-09-04 실측).
  **매칭 규칙을 안 밝힌 수치는 재현될 수 없다** — 넘길 때 SQL을 같이 넘긴다.
- **pull 리듬이 코드 한 곳에 앉았다.** `doomemacs-config` 가 `my/forge-pull-all` 을 만들어 줬다
  (`lisp/project-config.el`, stale 기본 6시간). 호출: `emacsclient -s user --eval '(my/forge-pull-all)'`.
  **폴링해도 안전하다** — stale 아니면 API를 안 건드리고 0을 반환한다. 임계값 SSOT는 그 집이다.
  강제 pull 실측(그 집): issues 148 → 164, open 53 → 57, `max(updated)` 가 오늘 것까지 왔다.
- **read-only 접속 허가받았다** — `file:<db>?mode=ro`, 조건 셋: `immutable=1` 절대 금지(락을 무시해
  쓰기 중 페이지를 찢어 읽는다) · `.timeout 5000` · **집계는 raw sqlite로**(emacsql 벡터 DSL은
  `[:select (max updated)]` 를 조용히 `SELECT updated` 로 컴파일한다 — 에러가 아니라 다른 답이 온다).
  `journal_mode=delete`, Forge 쪽 `busy_timeout` 20초라 내 짧은 읽기가 Forge를 못 깨뜨린다.
- `gh api rate_limit` — core 5000/hr, used 0. **호출량은 안 아프다. 아픈 건 질의다.**
- **Forge는 Forgejo 이슈를 못 가져온다** — `forge-forgejo.el:29` 가 `forge-unusedapi-repository` 를
  상속하고 그 `forge--pull`(`forge-commands.el:173`)은 `magit-git-fetch` 뿐이다. URL 형식표일 뿐이고,
  `forge.junghanacs.com` open 11개는 DB에 없다. **Forge 하나로는 「깃허브에 갇히지 않는다」를 못 지킨다.**
- 설계: GitHub → forge DB **read-only** · Forgejo → REST 직접 · **세 번째 저장소는 만들지 않는다.**
  파생 사본을 만드는 순간 오늘 본 그 고장(갈라진 사본·죽은 포인터·낡은 실측)을 이 집이 짓는다.
- GLG의 어쏠로그 `20240828T194548` 의 실측(`repo 1 / issue 0`)은 낡았다. 그 노트는 GLG의 것이니
  고치는 손도 GLG다 — 사실만 넘겼다.

- **Read:** `AGENTS.md`(계약 전부) · 담당자 문서 `20260227T031800`(연대기 + 「어떻게」) ·
  원석 `20240705T144627`(왜) · 롤링 페이퍼 `20260408T120252`
- **Do not touch:**
  - **대상 목록을 스스로 넓히지 않는다.** 묻는 자리는 `문서 미정` 레인 하나다.
  - 남의 리포에 직접 커밋하지 않는다. 발견·명명·전달까지다.
  - 대장에 유도 가능한 사실을 적지 않는다. **판정은 적는다** — 그 갈림이 이 집의 규율이다.
  - **`곁노트:` 는 `근거` 칸의 마지막 절로 쓴다.** 순회가 그 말부터 칸 끝까지를 브리핑에 싣는다.
  - **forge DB에 쓰지 않는다.** 그 인박스는 GLG와 `doomemacs-config` 의 것이고, 읽기만 한다 —
    내가 따로 긁으면 GLG가 Magit에서 보는 뷰와 갈리고, 그때부터 서로 다른 판을 보며 이야기하게 된다.
  - **forge DB에 쓰지 않는다.** 읽기만 하고, `--immutable`/`immutable=1` 은 **절대 쓰지 않는다** —
    락과 변경 감지가 꺼지고 행 수가 시작 시점에 굳는다(SQLite 문서 · datasette#1870).
    그 파일은 GLG의 Emacs가 `forge-pull` 할 때마다 쓴다. 플래그 없는 기본 모드가 맞다.
  - `~/repos/work` 는 대상이 아니다. `cos` 도 아니다.
  - `agent-config` 에 이 스킬의 사본을 두지 않는다. 실물은 하나, 나머지는 링크.
  - `~/org` 커밋은 GLG와 org 레인의 손이다. 노트는 고치되 커밋하지 않는다.

# 열린 물음

- **`#담당자` 표시 형식이 두 모양이다.** `§sorge #담당자` 하나, `§repo: #담당자 <자세>` 다섯.
  표시는 사람이 읽는 표지이지 순회의 조회 수단이 아니므로 급하지 않다. 붙일 때 형식도 같이.
- **이슈 레인의 모양.** 순회가 리포 넘나드는 이슈 관계를 보게 될 텐데, 그것을 여기
  이슈로 옮기는가 아니면 브리핑에만 싣는가. 대장이 차고 나서 정한다.
- **오라클과 리포 수가 다르다.** oracle 52 / thinkpad 71. 대장이 대상을 들게 된 지금은
  판정이 같으므로 순회 결과도 같지만, 대상을 넓힐 때 후보가 기기마다 다르게 보일 수는 있다.
- **순회 주기.** 지금은 GLG가 부를 때만이다. 주기를 만들면 그 주기가 관리 대상이 되므로,
  필요가 실제로 아플 때까지 미룬다.
- **루프로 도는 형태.** OpenClaw 봇으로 도는 판본이 가능해 보인다. 지금 그 워크스페이스
  안에 틀을 넣는 것은 GLG가 원치 않는다(2026-09-04) — 결정이 아니라 현재 입장이다.
