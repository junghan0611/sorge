#!/usr/bin/env python3
"""sorge robomp — ON 스위치. GitHub 이슈 훅 → `sorge-label` 프로파일 루프.

WHY THIS EXISTS
----------------
`sorge#22` Phase 0: 이슈 사건이 매번 fresh 담당자 턴을 깨우고, 그 턴은 라벨
판정만 남기고 끝난다. 하네스는 새로 짓지 않는다 — OMP 의 RobOMP
(`~/repos/3rd/pi/oh-my-pi/python/robomp`) 가 입구다. 이 스크립트는 그 위에
얹는 **손잡이**다: RobOMP 를 켜고/끄고/보는 것만 한다. `sorge-label` 프로파일
자체(어떤 host tool 을 노출하는지, fresh 세션인지)는 fork 쪽 코드가 결정한다
(`ROBOMP_TASK_PROFILE`) — 여기서는 정의하지 않는다.

경계 — 이 스크립트가 절대 하지 않는 것
--------------------------------------
- LEDGER.md 파싱을 다시 구현하지 않는다. `board.ledger_houses()` 를 그대로
  쓴다 — 대장 파싱은 한 곳에만 있어야 한다(이 집의 규율).
- fork(oh-my-pi) 소스를 고치지 않는다. venv 에 editable 설치만 한다.
- 비밀값을 파일 밖으로 내지 않는다. `pass` 에서 읽어 0600 파일에만 쓰고,
  화면에는 절대 찍지 않는다(dry-run 포함).
"""
import argparse
import json
import os
import re
import secrets
import shlex
import signal
import socket
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# 대장 파싱은 board.py 가 이미 든다 — 여기서 다시 만들지 않는다. 심링크로
# 도달해도 뿌리가 흔들리지 않는 이유는 board.py 의 docstring(realpath 8/8)과
# 같다.
HERE = os.path.dirname(os.path.realpath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import board  # noqa: E402

OWNER = board.OWNER

HOME = Path.home()
CONFIG_DIR = HOME / ".config" / "sorge"
STATE_DIR = HOME / ".local" / "state" / "sorge" / "robomp"
LOG_DIR = STATE_DIR / "logs"
DATA_DIR = HOME / ".local" / "share" / "sorge" / "robomp"
CACHE_DIR = HOME / ".cache" / "sorge"
VENV_DIR = CACHE_DIR / "robomp-venv"
ROBOMP_ENV = CONFIG_DIR / "robomp.env"
PROXY_ENV = CONFIG_DIR / "robomp-proxy.env"

ORCH_HOST = "127.0.0.1"
ORCH_PORT = 8080
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 8081

DEFAULT_OMP_ROOT = HOME / "repos" / "3rd" / "pi" / "oh-my-pi"
DEFAULT_AGENT_DIR = HOME / ".omp" / "agent"

# 봇 계정 토큰: orchestrator/gh-proxy 가 매일 쓰는 것. 판정은 sorge-bot 이름으로
# 남아야 하고, 그래야 자기재기동 가드(`ROBOMP_SELF_LOGINS`)가 GLG 가 연 이슈를
# 삼키지 않는다. classic: `gh webhook forward` 만 (admin:repo_hook 이 거기에만
# 있고, 후크 등록은 리포 소유자인 GLG 의 권한이다).
BOT_LOGIN = "sorge-bot"
PASS_PAT_BOT = "api/github/sorge-bot/pat"
PASS_PAT_CLASSIC = "api/github/junghan0611/forge/pat"

SECRET_KEYS = {"GITHUB_WEBHOOK_SECRET", "ROBOMP_GH_PROXY_HMAC_KEY", "GITHUB_TOKEN"}


class Halt(Exception):
    """`on --go` 가 이 자리에서 멈춘다 — 사유는 메시지에 있다."""


# ── 작은 도구들 ──────────────────────────────────────────────────────────


def omp_root() -> Path:
    return Path(os.environ.get("SORGE_OMP_ROOT", str(DEFAULT_OMP_ROOT))).expanduser()


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def port_alive(host, port, timeout=1.0):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def pidfile_path(name):
    return STATE_DIR / f"{name}.pid"


def read_pidfile(name):
    p = pidfile_path(name)
    if not p.exists():
        return None
    try:
        return int(p.read_text().strip())
    except ValueError:
        return None


def pid_alive(pid):
    return pid is not None and Path(f"/proc/{pid}").exists()


def proc_alive(name):
    pid = read_pidfile(name)
    return pid_alive(pid), pid


def forward_name(repo):
    return "webhook-forward-" + repo.replace("/", "-")


def parse_env_file(path):
    out = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip()
    return out


def render_env_file(values):
    lines = [
        "# sorge robomp — 생성: ./run.sh robomp on --go. 손으로 고치지 마라 (재실행이 덮는다).",
        "",
    ]
    lines += [f"{k}={v}" for k, v in values.items()]
    lines.append("")
    return "\n".join(lines)


def write_env_file(path, values):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_env_file(values), encoding="utf-8")
    os.chmod(path, 0o600)


def allowlist_repos():
    """대장 `배정` 리포 → `owner/repo` 목록. board.py 의 판정을 그대로 쓴다."""
    houses = board.ledger_houses()
    return [f"{OWNER}/{repo}" for repo in sorted(houses)]


def pass_show(path):
    r = sh(["pass", "show", path])
    if r.returncode != 0:
        raise RuntimeError(f"pass show {path} 실패: {(r.stderr or '').strip() or ('exit ' + str(r.returncode))}")
    val = r.stdout.strip()
    if not val:
        raise RuntimeError(f"pass show {path} 가 빈 값을 냈다")
    return val


def gh_api(token, method, path, body=None):
    """GitHub REST 한 번. 토큰은 헤더로만 간다 — argv 에 실으면 같은 사용자의
    다른 프로세스가 `ps` 로 줍는다."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "sorge-robomp",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read() or b"null")
    except urllib.error.HTTPError as exc:
        try:
            return exc.code, json.loads(exc.read() or b"null")
        except ValueError:
            return exc.code, None
    except urllib.error.URLError as exc:
        raise RuntimeError(f"GitHub 도달 실패: {exc.reason}") from exc


def bot_token_check(dry, token, repos):
    """봇 토큰이 **그 이름으로 라벨을 쓸 수 있는가** — 비파괴로 묻는다.

    읽기는 신호가 아니다. 대상 리포가 전부 public 이라 토큰이 없어도 200 이
    나온다. 쓰기만 신호다.

    그리고 여기서 갈리는 것이 하나 있다: fine-grained PAT 는 **발급 계정이
    소유한** 리포에만 권한을 줄 수 있다. collaborator 로 초대돼 push 권한이
    있어도 GLG 소유 리포에는 `403 Resource not accessible by personal access
    token` 이 난다(2026-09-15 실측). 그래서 봇 토큰은 classic + `public_repo`
    여야 하고, 그 구분이 이 자리에서 드러나야 한다 — 프로세스를 띄운 뒤
    첫 판정이 403 으로 죽는 것보다 낫다.
    """
    status, who = gh_api(token, "GET", "/user")
    login = (who or {}).get("login") if status == 200 else None
    check(
        dry,
        login == BOT_LOGIN,
        f"토큰 주인 = {login}",
        f"토큰 주인이 {login or f'불명({status})'} 이다 — {BOT_LOGIN} 이어야 한다",
    )

    probe = repos[0]
    status, labels = gh_api(token, "GET", f"/repos/{probe}/labels?per_page=1")
    if status != 200 or not isinstance(labels, list) or not labels:
        check(dry, False, "", f"{probe} 라벨 목록을 못 읽는다 ({status}) — 리포/초대 확인")
        return
    current = labels[0]
    # 같은 값으로 PATCH: 상태를 바꾸지 않고 권한만 묻는다.
    body = {k: current[k] for k in ("name", "color", "description") if k in current}
    status, err = gh_api(token, "PATCH", f"/repos/{probe}/labels/{current['name']}", body)
    check(
        dry,
        status == 200,
        f"{probe} 라벨 쓰기 가능 (무변경 PATCH 200)",
        f"{probe} 라벨 쓰기 거부 ({status} {(err or {}).get('message', '')}) — "
        f"fine-grained PAT 는 남의 소유 리포에 쓸 수 없다. {BOT_LOGIN} 으로 로그인해 "
        f"classic token(scope: public_repo 하나)을 만들고 `pass insert {PASS_PAT_BOT}` 로 덮어써라",
    )


def check(dry, cond, ok_msg, fail_msg):
    """전제 하나를 찍는다. `--go` 에서 실패하면 그 자리에서 멈춘다."""
    if cond:
        print(f"   ✓ {ok_msg}")
        return True
    print(f"   ✗ {fail_msg}")
    if not dry:
        raise Halt(fail_msg)
    return False


def attempt(dry, label, fn):
    """fn() 을 실행하고 영수증을 찍는다. `--go` 에서 실패하면 멈춘다."""
    try:
        result = fn()
        print(f"   ✓ {label}")
        return result
    except Exception as exc:  # noqa: BLE001 — 원인 그대로 사유에 싣는다
        print(f"   ✗ {label} 실패: {exc}")
        if not dry:
            raise Halt(f"{label} 실패: {exc}") from exc
        return None


def launch(cmd, *, cwd, env, log_path, pidname):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    pidfile_path(pidname).parent.mkdir(parents=True, exist_ok=True)
    logf = open(log_path, "ab")
    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd),
        env=env,
        stdout=logf,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        start_new_session=True,  # setsid 동격 — 이 세션이 끝나도 산다
    )
    pidfile_path(pidname).write_text(str(proc.pid))
    return proc.pid


def wait_port(host, port, timeout, label):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if port_alive(host, port):
            print(f"   ✓ {label} 준비됨 — {host}:{port}")
            return
        time.sleep(0.5)
    raise Halt(f"{label} 이(가) {timeout}초 안에 {host}:{port} 를 열지 않았다 — 로그를 봐라")


def wait_http_ok(url, timeout, label):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:  # noqa: S310
                if resp.status < 500:
                    print(f"   ✓ {label} 준비됨 — {url} → {resp.status}")
                    return
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(0.5)
    raise Halt(f"{label} 이(가) {timeout}초 안에 {url} 로 응답하지 않았다 — 로그를 봐라")


def wait_log(log_path, pattern, timeout, label):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if log_path.exists():
            text = log_path.read_text(encoding="utf-8", errors="replace")
            if pattern.search(text):
                print(f"   ✓ {label} 준비됨 — 로그: {log_path}")
                return
        time.sleep(0.5)
    raise Halt(f"{label} 이(가) {timeout}초 안에 준비 신호를 안 냈다 — 로그를 봐라: {log_path}")


# ── status ───────────────────────────────────────────────────────────────


def cmd_status(_args):
    print("━━ sorge robomp · 상태 ━━\n")

    proxy_up = port_alive(PROXY_HOST, PROXY_PORT)
    orch_up = port_alive(ORCH_HOST, ORCH_PORT)
    print(f"  gh-proxy      {'떠 있음' if proxy_up else '내려 있음'} — {PROXY_HOST}:{PROXY_PORT}")
    print(f"  orchestrator  {'떠 있음' if orch_up else '내려 있음'} — {ORCH_HOST}:{ORCH_PORT}")

    cfg = parse_env_file(ROBOMP_ENV)
    print()
    if not cfg:
        print(f"  config 없음 — {ROBOMP_ENV} 가 아직 없다. `./run.sh robomp on --go` 로 켠다.")
        repos = []
    else:
        print(f"  profile       {cfg.get('ROBOMP_TASK_PROFILE', '?')}")
        print(f"  model         {cfg.get('ROBOMP_MODEL', '?')}  (thinking={cfg.get('ROBOMP_THINKING', '?')})")
        print(f"  agent dir     {cfg.get('ROBOMP_AGENT_DIR', '?')}")
        print(f"  self logins   {cfg.get('ROBOMP_SELF_LOGINS', '?')}")
        allow = cfg.get("ROBOMP_REPO_ALLOWLIST", "")
        print(f"  allowlist     {allow or '(비었다)'}")
        repos = [r for r in allow.split(",") if r]

    print()
    if not cfg:
        print("  gh webhook forward: 대상 없음 (config 없음)")
    elif not repos:
        print("  gh webhook forward: 대상 없음 (allowlist 가 비었다)")
    else:
        print("  gh webhook forward:")
        for repo in repos:
            alive, pid = proc_alive(forward_name(repo))
            print(f"    {repo:<32} {'떠 있음 (pid ' + str(pid) + ')' if alive else '안 떠 있음'}")

    sqlite_path = Path(cfg["ROBOMP_SQLITE_PATH"]) if cfg.get("ROBOMP_SQLITE_PATH") else (DATA_DIR / "robomp.sqlite")
    print()
    if not sqlite_path.exists():
        print(f"  최근 이벤트 없음 — sqlite 가 아직 없다 ({sqlite_path})")
    else:
        try:
            con = sqlite3.connect(f"file:{sqlite_path}?mode=ro", uri=True)
            con.row_factory = sqlite3.Row
            rows = con.execute(
                "SELECT delivery_id, event_type, repo, issue_key, state, received_at "
                "FROM events ORDER BY received_at DESC LIMIT 5"
            ).fetchall()
            con.close()
        except sqlite3.Error as exc:
            print(f"  이벤트 조회 실패: {sqlite_path} — {exc}")
            rows = None
        if rows is not None:
            if rows:
                print(f"  최근 이벤트 (最대 5, {sqlite_path}):")
                for row in rows:
                    print(
                        f"    {row['received_at']}  {row['state']:<8} {row['event_type']:<16} "
                        f"{row['repo'] or '-':<28} {row['issue_key'] or ''}"
                    )
            else:
                print(f"  최근 이벤트 없음 — events 표가 비었다 ({sqlite_path})")

    if not proxy_up and not orch_up and not cfg:
        print("\n  아무것도 안 돌고 있다.")


# ── allowlist ────────────────────────────────────────────────────────────


def cmd_allowlist(_args):
    repos = allowlist_repos()
    print(f"━━ sorge robomp · allowlist · 대장 배정 {len(repos)}집 ━━\n")
    for r in repos:
        print(f"  {r}")
    print()
    print(f"ROBOMP_REPO_ALLOWLIST={','.join(repos)}")


# ── on ───────────────────────────────────────────────────────────────────


def _on_steps(dry):
    root = omp_root()
    robomp_src = root / "python" / "robomp"
    omprpc_src = root / "python" / "omp-rpc"

    print("1) fork 확인")
    check(
        dry,
        robomp_src.is_dir() and omprpc_src.is_dir(),
        f"{root}  (python/robomp, python/omp-rpc 둘 다 있다)",
        f"{root} 에 python/robomp 또는 python/omp-rpc 가 없다 — SORGE_OMP_ROOT 로 덮어써라",
    )

    print("\n2) gh 확장 확인")
    ext = sh(["gh", "extension", "list"])
    has_webhook_ext = ext.returncode == 0 and "gh webhook" in ext.stdout
    check(
        dry,
        has_webhook_ext,
        "gh webhook 확장 설치됨",
        "gh webhook 확장이 없다 — `gh extension install cli/gh-webhook`",
    )

    print("\n3) venv 준비")
    pyexe = str(VENV_DIR / "bin" / "python")
    pip = str(VENV_DIR / "bin" / "pip")
    if VENV_DIR.exists():
        print(f"   ✓ 이미 있다: {VENV_DIR}")
    else:
        print(f"   {'만들 것' if dry else '만든다'}: python3 -m venv {VENV_DIR}")
        print(f"   {'설치할 것' if dry else '설치한다'}: pip install -e {omprpc_src}  (pip only — AGENTS.md)")
        print(f"   {'설치할 것' if dry else '설치한다'}: pip install -e {robomp_src}")
        if not dry:
            r = sh(["python3", "-m", "venv", str(VENV_DIR)])
            if r.returncode != 0:
                raise Halt(f"venv 생성 실패: {r.stderr.strip()}")
            for target in (omprpc_src, robomp_src):
                r = sh([pip, "install", "-e", str(target)])
                if r.returncode != 0:
                    raise Halt(f"pip install -e {target} 실패: {r.stderr.strip()[-800:]}")
            print(f"   ✓ venv 준비됨: {VENV_DIR}")

    print("\n4) 대장 → allowlist 유도 (board.ledger_houses() 재사용)")
    # board.py 가 대장을 못 읽으면 여기서 sys.exit 로 바로 멈춘다 — 빈 대장을
    # "빚 0" 처럼 조용히 삼키지 않는 것이 board.py 의 규율이고, 여기서도 그대로다.
    allow_repos = allowlist_repos()
    check(dry, len(allow_repos) > 0, f"배정 {len(allow_repos)}집 → {','.join(allow_repos)}", "대장에 배정된 리포가 없다 — LEDGER.md 확인")

    print("\n5) 경로 확보 (절대경로 — 상대경로면 worktree pool 이 cwd 기준으로 풀려 깨진다)")
    workspace_root = DATA_DIR / "workspaces"
    sqlite_path = DATA_DIR / "robomp.sqlite"
    app_log_dir = DATA_DIR / "logs"
    natives_root = DATA_DIR / "cache" / "pi-natives"
    for p in (workspace_root, sqlite_path.parent, app_log_dir, natives_root):
        print(f"   {'만들 것' if dry else '만든다'}: {p}")
        if not dry:
            p.mkdir(parents=True, exist_ok=True)

    print("\n6) 설정 파일: " + str(ROBOMP_ENV))
    existing = parse_env_file(ROBOMP_ENV)
    webhook_secret = existing.get("GITHUB_WEBHOOK_SECRET") or secrets.token_hex(32)
    hmac_key = existing.get("ROBOMP_GH_PROXY_HMAC_KEY") or secrets.token_hex(32)
    print(f"   GITHUB_WEBHOOK_SECRET     {'재사용' if 'GITHUB_WEBHOOK_SECRET' in existing else '새로 생성'} (값은 안 찍는다)")
    print(f"   ROBOMP_GH_PROXY_HMAC_KEY  {'재사용' if 'ROBOMP_GH_PROXY_HMAC_KEY' in existing else '새로 생성'} (값은 안 찍는다)")
    values = {
        "GITHUB_WEBHOOK_SECRET": webhook_secret,
        "ROBOMP_BOT_LOGIN": BOT_LOGIN,
        # config.py 의 orchestrator Settings 는 이 둘을 필수로 요구한다
        # (`git_author_email: str = Field(..., ...)`, 기본값 없음). `sorge-label`
        # 프로파일은 gh_push_branch 를 쓰지 않아 실사용은 안 되지만, Settings()
        # 생성 자체가 이 값 없이는 즉시 실패한다 — 그래서 계약 표엔 없어도 넣는다.
        "ROBOMP_GIT_AUTHOR_NAME": existing.get("ROBOMP_GIT_AUTHOR_NAME", "sorge-robomp"),
        "ROBOMP_GIT_AUTHOR_EMAIL": existing.get("ROBOMP_GIT_AUTHOR_EMAIL", "sorge-robomp@users.noreply.github.com"),
        "ROBOMP_SELF_LOGINS": BOT_LOGIN,
        "ROBOMP_TASK_PROFILE": "sorge-label",
        "ROBOMP_MODEL": "anthropic/claude-sonnet-4-6",
        "ROBOMP_THINKING": "high",
        "ROBOMP_AGENT_DIR": str(DEFAULT_AGENT_DIR),
        "ROBOMP_REPO_ALLOWLIST": ",".join(allow_repos),
        "ROBOMP_GH_PROXY_URL": f"http://{PROXY_HOST}:{PROXY_PORT}",
        "ROBOMP_GH_PROXY_HMAC_KEY": hmac_key,
        "ROBOMP_WORKSPACE_ROOT": str(workspace_root),
        "ROBOMP_SQLITE_PATH": str(sqlite_path),
        "ROBOMP_LOG_DIR": str(app_log_dir),
        "ROBOMP_NATIVES_CACHE_ROOT": str(natives_root),
        "ROBOMP_PR_REVIEW_ENABLED": "false",
        "ROBOMP_QUESTION_AUTOCLOSE_ENABLED": "false",
        "ROBOMP_RELEASE_SENTINEL_ENABLED": "false",
        "ROBOMP_BIND_HOST": ORCH_HOST,
        "ROBOMP_BIND_PORT": str(ORCH_PORT),
    }
    for k, v in values.items():
        if k in SECRET_KEYS:
            continue
        print(f"   {k}={v}")
    if dry:
        print(f"   [dry-run] {ROBOMP_ENV} 쓰지 않음 (0600 이 될 것)")
    else:
        write_env_file(ROBOMP_ENV, values)
        print(f"   ✓ 썼다: {ROBOMP_ENV} (0600)")

    print("\n7) 설정 파일: " + str(PROXY_ENV))
    token = attempt(dry, f"pass {PASS_PAT_BOT} 읽기", lambda: pass_show(PASS_PAT_BOT))
    if token:
        bot_token_check(dry, token, allow_repos)
    if dry:
        print(f"   [dry-run] {PROXY_ENV} 쓰지 않음 (0600, GITHUB_TOKEN 하나만 담을 것)")
    else:
        write_env_file(PROXY_ENV, {"GITHUB_TOKEN": token})
        print(f"   ✓ 썼다: {PROXY_ENV} (0600, GITHUB_TOKEN 하나)")

    print("\n8) 포트 확인")
    check(dry, not port_alive(PROXY_HOST, PROXY_PORT), f"{PROXY_HOST}:{PROXY_PORT} 비어 있음", f"{PROXY_HOST}:{PROXY_PORT} 이미 점유 — 먼저 `off` 하거나 그 프로세스를 확인해라")
    check(dry, not port_alive(ORCH_HOST, ORCH_PORT), f"{ORCH_HOST}:{ORCH_PORT} 비어 있음", f"{ORCH_HOST}:{ORCH_PORT} 이미 점유 — 먼저 `off` 하거나 그 프로세스를 확인해라")

    print("\n9) gh-proxy 기동")
    proxy_cmd = [pyexe, "-m", "robomp.proxy", "serve"]
    proxy_log = LOG_DIR / "gh-proxy.log"
    print(f"   {'띄울 것' if dry else '띄운다'}: {' '.join(shlex.quote(c) for c in proxy_cmd)}")
    print(f"     cwd={robomp_src}")
    print(f"     env: GITHUB_TOKEN(proxy 전용) · ROBOMP_GH_PROXY_HMAC_KEY · ROBOMP_WORKSPACE_ROOT · ROBOMP_LOG_DIR")
    print(f"     bind: ROBOMP_GH_PROXY_BIND_HOST={PROXY_HOST} ROBOMP_GH_PROXY_BIND_PORT={PROXY_PORT}")
    print(f"     로그: {proxy_log}  pidfile: {pidfile_path('gh-proxy')}")
    print(f"     준비 관측: {PROXY_HOST}:{PROXY_PORT} 접속 성공 (최대 30초)")
    if not dry:
        proxy_env = dict(os.environ)
        proxy_env.update(parse_env_file(ROBOMP_ENV))  # HMAC key, workspace/log 경로 공유
        proxy_env.update(parse_env_file(PROXY_ENV))  # GITHUB_TOKEN
        proxy_env["ROBOMP_GH_PROXY_BIND_HOST"] = PROXY_HOST
        proxy_env["ROBOMP_GH_PROXY_BIND_PORT"] = str(PROXY_PORT)
        launch(proxy_cmd, cwd=robomp_src, env=proxy_env, log_path=proxy_log, pidname="gh-proxy")
        wait_port(PROXY_HOST, PROXY_PORT, 30, "gh-proxy")

    print("\n10) orchestrator 기동")
    orch_cmd = [pyexe, "-m", "robomp", "serve"]
    orch_log = LOG_DIR / "orchestrator.log"
    print(f"   {'띄울 것' if dry else '띄운다'}: {' '.join(shlex.quote(c) for c in orch_cmd)}")
    print(f"     cwd={robomp_src}  env: {ROBOMP_ENV} 전체 (GITHUB_TOKEN 은 안 준다 — serve 가 거부한다)")
    print(f"     bind: ROBOMP_BIND_HOST={ORCH_HOST} ROBOMP_BIND_PORT={ORCH_PORT}")
    print(f"     로그: {orch_log}  pidfile: {pidfile_path('orchestrator')}")
    print(f"     준비 관측: GET http://{ORCH_HOST}:{ORCH_PORT}/healthz (최대 30초)")
    if not dry:
        orch_env = dict(os.environ)
        orch_env.update(parse_env_file(ROBOMP_ENV))
        orch_env.pop("GITHUB_TOKEN", None)  # serve() 가 이걸 보면 SystemExit — 절대 안 준다
        launch(orch_cmd, cwd=robomp_src, env=orch_env, log_path=orch_log, pidname="orchestrator")
        wait_http_ok(f"http://{ORCH_HOST}:{ORCH_PORT}/healthz", 30, "orchestrator")

    print(f"\n11) gh webhook forward ({len(allow_repos)}개 리포, --events=issues)")
    classic_pat = attempt(dry, f"pass {PASS_PAT_CLASSIC} 읽기 (admin:repo_hook, forward 전용)", lambda: pass_show(PASS_PAT_CLASSIC))
    for repo in allow_repos:
        name = forward_name(repo)
        fwd_log = LOG_DIR / f"{name}.log"
        printable = [
            "gh", "webhook", "forward",
            f"--repo={repo}", "--events=issues",
            f"--url=http://{ORCH_HOST}:{ORCH_PORT}/webhook/github",
            "--secret=***",
        ]
        print(f"   {'띄울 것' if dry else '띄운다'}: {' '.join(printable)}")
        print(f"     env: GH_TOKEN=<forge classic PAT>  로그: {fwd_log}  pidfile: {pidfile_path(name)}")
        print(f"     준비 관측: 로그에 forward/listen 신호 (최대 20초)")
        if not dry:
            real_cmd = [
                "gh", "webhook", "forward",
                f"--repo={repo}", "--events=issues",
                f"--url=http://{ORCH_HOST}:{ORCH_PORT}/webhook/github",
                f"--secret={webhook_secret}",
            ]
            fwd_env = dict(os.environ)
            fwd_env["GH_TOKEN"] = classic_pat
            launch(real_cmd, cwd=robomp_src, env=fwd_env, log_path=fwd_log, pidname=name)
            wait_log(fwd_log, re.compile(r"[Ff]orward|[Ll]isten|[Cc]onnect"), 20, name)

    print()
    if dry:
        print("dry-run 끝 — 실제로 켜려면 `./run.sh robomp on --go`")
    else:
        print("✓ 켰다. `./run.sh robomp status` 로 확인해라.")


def cmd_on(args):
    dry = not args.go
    print(f"━━ sorge robomp · on · {'dry-run (--go 로 실제 실행)' if dry else '실행'} ━━\n")
    try:
        _on_steps(dry)
    except Halt as exc:
        print(f"\n멈췄다: {exc}")
        sys.exit(1)


# ── off ──────────────────────────────────────────────────────────────────


def cmd_off(_args):
    print("━━ sorge robomp · off ━━\n")
    cfg = parse_env_file(ROBOMP_ENV)
    repos = [r for r in cfg.get("ROBOMP_REPO_ALLOWLIST", "").split(",") if r]
    names = ["orchestrator", "gh-proxy"] + [forward_name(r) for r in repos]
    # 대장이 줄어든 뒤에도 남았을 pidfile 을 놓치지 않는다.
    if STATE_DIR.exists():
        for p in STATE_DIR.glob("webhook-forward-*.pid"):
            if p.stem not in names:
                names.append(p.stem)

    any_running = False
    for name in names:
        alive, pid = proc_alive(name)
        if not alive:
            continue
        any_running = True
        print(f"  {name}: SIGTERM → pid {pid}")
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        for _ in range(20):
            if not pid_alive(pid):
                break
            time.sleep(0.5)
        if pid_alive(pid):
            print("    안 죽는다 → SIGKILL")
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        print("    ✓ 내렸다")
        pidfile_path(name).unlink(missing_ok=True)

    if not any_running:
        print("  이미 꺼져 있다.")


# ── main ─────────────────────────────────────────────────────────────────


def main():
    ap = argparse.ArgumentParser(description="sorge robomp — 이슈 훅 루프 ON 스위치")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("status", help="gh-proxy/orchestrator/webhook forward 생사 + allowlist + 최근 이벤트")
    sub.add_parser("allowlist", help="LEDGER.md 배정 리포 → owner/repo 목록 (board.ledger_houses 재사용)")
    p_on = sub.add_parser("on", help="venv → env 파일 → gh-proxy → orchestrator → webhook forward 순서로 켠다")
    p_on.add_argument("--go", action="store_true", help="실제로 켠다 (기본은 dry-run — 아무 부작용 없이 계획만 찍는다)")
    sub.add_parser("off", help="pidfile 기준으로 전부 정상 종료한다 (SIGTERM → 확인 → SIGKILL)")
    a = ap.parse_args()

    if a.cmd == "status":
        cmd_status(a)
    elif a.cmd == "allowlist":
        cmd_allowlist(a)
    elif a.cmd == "on":
        cmd_on(a)
    elif a.cmd == "off":
        cmd_off(a)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
