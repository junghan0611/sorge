#!/usr/bin/env bash
# sorge — 돌봄의 순회를 손으로 부르는 자리
#
# 이 스크립트는 SSOT 가 아니다. 판정은 LEDGER.md 가 들고, 순회 논리는
# .claude/skills/sorge/scripts/sweep.py 가 든다. 여기 사는 것은 그 둘을
# 부르는 손잡이뿐이다 — 명령을 외우지 않아도 되게.
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()    { echo -e "${BLUE}ℹ ${NC}$1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }
warn()    { echo -e "${YELLOW}⚠${NC} $1"; }
error()   { echo -e "${RED}✗${NC} $1"; }

SORGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SWEEP="$SORGE_DIR/.claude/skills/sorge/scripts/sweep.py"
BOARD="$SORGE_DIR/.claude/skills/sorge/scripts/board.py"
LABELS="$SORGE_DIR/.claude/skills/sorge/scripts/labels.py"
ROBOMP="$SORGE_DIR/.claude/skills/sorge/scripts/robomp.py"
BOARD_PORT="${SORGE_BOARD_PORT:-8071}"

# 이슈판이 얹히는 DB. 이 집 것이 아니다 -- Magit Forge 가 쓰는 GLG 의 로컬
# 캐시이고 소유는 doomemacs-config 다. 읽기만 한다.
FORGE_DB="$HOME/doomemacs/.local/etc/forge/forge-database.sqlite"

need() {
    command -v "$1" >/dev/null 2>&1 && return 0
    error "$1 is missing. $2"
    return 1
}

# ── 순회 ────────────────────────────────────────────────

sweep_board() { python3 "$SWEEP" "$@"; }

# 이슈판 — 라이브. 저장하지 않는다. 상태는 이슈 라벨에 산다.
board_show()  { python3 "$BOARD" "$@"; }
board_label() { python3 "$LABELS" "$@"; }
board_robomp() { python3 "$ROBOMP" "$@"; }

sweep_brief() {
    local repo="${1:-}"
    if [[ -n "$repo" ]]; then
        python3 "$SWEEP" --repo "$repo" --brief
    else
        python3 "$SWEEP" --brief
    fi
}

# ── 이슈판 ──────────────────────────────────────────────

board_pid() { ss -ltnp 2>/dev/null | grep -oP "(?<=pid=)\d+(?=,fd)" <<<"$(ss -ltnp 2>/dev/null | grep ":$BOARD_PORT ")" | head -1; }

board_status() {
    local pid; pid="$(board_pid || true)"
    if [[ -n "$pid" ]]; then
        success "lens up — http://127.0.0.1:$BOARD_PORT (pid $pid)"
        return 0
    fi
    info "lens down (port $BOARD_PORT)"
    return 1
}

board_start() {
    need datasette "nixos-config puts it on the first floor — ask that steward." || return 1
    [[ -f "$FORGE_DB" ]] || { error "forge DB missing: $FORGE_DB"; return 1; }

    if board_status >/dev/null 2>&1; then
        board_status
        warn "already up. stop it first to relaunch."
        return 0
    fi

    # --immutable 을 붙이지 않는다. 그 플래그는 "이 파일은 안 바뀐다" 를
    # 전제해 락과 변경 감지를 끄고 행 수를 시작 시점에 굳힌다. 이 파일은
    # GLG 의 Emacs 가 forge-pull 할 때마다 바뀐다 (SQLite 문서 · datasette#1870).
    setsid nohup datasette serve "$FORGE_DB" \
        -m "$METADATA" --port "$BOARD_PORT" \
        > /tmp/sorge-board.log 2>&1 < /dev/null &
    sleep 4

    if curl -sf -m 5 -o /dev/null "http://127.0.0.1:$BOARD_PORT/"; then
        success "lens → http://127.0.0.1:$BOARD_PORT"
        echo ""
        echo "  open board   /forge-database/board"
        echo "  by repo      /forge-database/by_repo"
        echo "  stale open   /forge-database/stale_open"
        echo ""
        info "log: /tmp/sorge-board.log"
    else
        error "did not come up. read the log: /tmp/sorge-board.log"
        tail -5 /tmp/sorge-board.log 2>/dev/null || true
        return 1
    fi
}

board_stop() {
    local pid; pid="$(board_pid || true)"
    if [[ -z "$pid" ]]; then info "already down."; return 0; fi
    kill "$pid" && success "lens down (pid $pid)"
}

board_pull() {
    # pull 리듬은 이 집이 쥐지 않는다. 정책은 doomemacs-config 의
    # my/forge-stale-p (기본 6시간) 가 SSOT 이고, 여기서는 부르기만 한다.
    # stale 아니면 API 를 안 건드리고 0 을 반환한다 -- 폴링해도 안전하다.
    local force="${1:-}"
    local call="(my/forge-pull-all)"
    [[ "$force" == "force" ]] && call="(my/forge-pull-all t)"
    info "forge-pull: $call"
    if ! timeout 180 emacsclient -s user --eval "$call"; then
        error "GLG's Emacs (user socket) is not answering. that one is a human's seat."
        return 1
    fi
}

board_age() {
    [[ -f "$FORGE_DB" ]] || { error "forge DB missing"; return 1; }
    local mt now hrs
    mt=$(stat -c %Y "$FORGE_DB"); now=$(date +%s)
    hrs=$(( (now - mt) / 3600 ))
    echo "  DB updated: $(date -d "@$mt" '+%Y-%m-%d %H:%M')  (${hrs}h ago)"
    sqlite3 -cmd '.timeout 5000' "file:$FORGE_DB?mode=ro" \
        "select '  repos '||count(distinct repository)||' · open '||sum(state='open')||' · total '||count(*) from issue"
}

# ── 메뉴 ────────────────────────────────────────────────

show_menu() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}sorge${NC} — leap ahead, never leap in"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "  ${YELLOW}Sweep${NC}"
    echo "    i) issue board (live · labels are the state)"
    echo "    1) sweep (debt · undecided docs · out of scope)"
    echo "    2) brief all (blocks to hand a sibling as-is)"
    echo "    3) brief one repo (answers even out of scope)"
    echo "    4) sweep with another debt threshold (default 15)"
    echo ""
    echo -e "  ${YELLOW}Issue loop (stock RobOMP · sorge-bot)${NC}"
    echo "    5) status — proxy/orchestrator/forwarders, model, allowlist"
    echo "    6) on (dry-run — prints what it would do)"
    echo "    7) on --go (venv → env → proxy → orchestrator → forwarders)"
    echo "    N) on --go, narrowed to one repo (while a new model settles in)"
    echo "    8) off (stop everything, delete relay hooks)"
    echo "    9) judge one issue by hand (owner/repo#NN)"
    echo ""
    echo -e "  ${YELLOW}Forge lens (Magit Forge cache · read-only)${NC}"
    echo "    b) datasette lens → http://127.0.0.1:$BOARD_PORT"
    echo "    s) lens status"
    echo "    q) lens down"
    echo "    a) DB age and size"
    echo "    p) forge-pull (only when stale)"
    echo "    P) forge-pull (forced)"
    echo ""
    echo -e "  ${YELLOW}Ledger${NC}"
    echo "    l) open LEDGER.md"
    echo "    n) open NEXT.md"
    echo ""
    echo "    0) quit"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

usage() {
    cat <<EOF
sorge — the caretaker sweep

  ./run.sh                 interactive menu
  ./run.sh sweep [args…]   sweep. args pass straight to sweep.py
  ./run.sh brief [repo]    briefing block(s)
  ./run.sh board [args…]   live issue board (gh + ledger join). --debt --house R --mine [R] --all --json
  ./run.sh label --set 'R#N=ready,owner,important-urgent,steward-ready' --go
                           lifecycle transition (single-value axes; priority:none/brief:none withdraws)
  ./run.sh label --house 'R#N=house' --go        pin whose share it is
  ./run.sh label --ensure                        define labels (dry-run by default)
  ./run.sh lens            datasette lens (Magit Forge cache · read-only)
  ./run.sh lens-stop       lens down
  ./run.sh lens-status     lens status
  ./run.sh age             DB age and size
  ./run.sh pull [force]    forge-pull (policy owned by doomemacs-config)

Issue loop — stock RobOMP, no fork patches:
  ./run.sh robomp status              proxy/orchestrator/forwarder liveness, model, allowlist, recent events
  ./run.sh robomp allowlist           ledger-assigned repos → owner/repo (reuses ledger_houses)
  ./run.sh robomp on [--go]           venv → env → gh-proxy → orchestrator → forwarders (dry-run by default)
  ./run.sh robomp on --go --only sorge   same, narrowed to a few repos for this start only (ledger untouched)
  ./run.sh robomp off                 stop everything by pidfile, delete relay hooks
  ./run.sh robomp judge owner/repo#NN  queue one issue by hand, no webhook needed

The ledger holds the verdicts. This script is only a handle.
EOF
}

main() {
    if [[ $# -gt 0 ]]; then
        case "$1" in
            sweep)        shift; sweep_board "$@" ;;
            brief)        shift; sweep_brief "${1:-}" ;;
            board)        shift; board_show "$@" ;;
            label)        shift; board_label "$@" ;;
            lens)         board_start ;;
            lens-stop)    board_stop ;;
            lens-status)  board_status ;;
            age)          board_age ;;
            pull)         shift; board_pull "${1:-}" ;;
            robomp)       shift; board_robomp "$@" ;;
            -h|--help|help) usage ;;
            *)            error "unknown command: $1"; echo ""; usage; exit 1 ;;
        esac
        return
    fi

    while true; do
        show_menu
        read -rp "choice: " choice
        echo ""
        case $choice in
            1) sweep_board ;;
            2) sweep_brief ;;
            3) read -rp "repo name: " r; [[ -n "$r" ]] && sweep_brief "$r" ;;
            4) read -rp "debt threshold (commits): " d; [[ -n "$d" ]] && sweep_board --debt "$d" ;;
            i) board_show ;;
            5) board_robomp status ;;
            6) board_robomp on ;;
            7) board_robomp on --go ;;
            N) read -rp "repo(s), comma-separated (e.g. sorge): " r; [[ -n "$r" ]] && board_robomp on --go --only "$r" ;;
            8) board_robomp off ;;
            9) read -rp "issue ref (owner/repo#NN): " ref; [[ -n "$ref" ]] && board_robomp judge "$ref" ;;
            b) board_start ;;
            s) board_status || true ;;
            q) board_stop ;;
            a) board_age ;;
            p) board_pull ;;
            P) board_pull force ;;
            l) ${PAGER:-less} "$SORGE_DIR/LEDGER.md" ;;
            n) ${PAGER:-less} "$SORGE_DIR/NEXT.md" ;;
            0) info "bye."; exit 0 ;;
            *) error "invalid choice" ;;
        esac
        echo ""
        read -rp "press Enter to continue…"
    done
}

main "$@"
