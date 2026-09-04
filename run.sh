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
METADATA="$SORGE_DIR/datasette/metadata.yml"
BOARD_PORT="${SORGE_BOARD_PORT:-8071}"

# 이슈판이 얹히는 DB. 이 집 것이 아니다 -- Magit Forge 가 쓰는 GLG 의 로컬
# 캐시이고 소유는 doomemacs-config 다. 읽기만 한다.
FORGE_DB="$HOME/doomemacs/.local/etc/forge/forge-database.sqlite"

need() {
    command -v "$1" >/dev/null 2>&1 && return 0
    error "$1 이(가) 없다. $2"
    return 1
}

# ── 순회 ────────────────────────────────────────────────

sweep_board() { python3 "$SWEEP" "$@"; }

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
        success "이슈판 떠 있다 — http://127.0.0.1:$BOARD_PORT (pid $pid)"
        return 0
    fi
    info "이슈판 안 떠 있다 (포트 $BOARD_PORT)"
    return 1
}

board_start() {
    need datasette "nixos-config 가 1층으로 넣는다 — 그 집 담당자에게." || return 1
    [[ -f "$FORGE_DB" ]] || { error "forge DB 가 없다: $FORGE_DB"; return 1; }

    if board_status >/dev/null 2>&1; then
        board_status
        warn "이미 떠 있다. 다시 띄우려면 stop 먼저."
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
        success "이슈판 → http://127.0.0.1:$BOARD_PORT"
        echo ""
        echo "  횡단 이슈   /forge-database/cross_repo   ← 다른 리포를 부르는 open 이슈"
        echo "  열린 판     /forge-database/board"
        echo "  리포별      /forge-database/by_repo"
        echo "  오래된 것   /forge-database/stale_open"
        echo ""
        info "로그: /tmp/sorge-board.log"
    else
        error "안 떴다. 로그를 봐라: /tmp/sorge-board.log"
        tail -5 /tmp/sorge-board.log 2>/dev/null || true
        return 1
    fi
}

board_stop() {
    local pid; pid="$(board_pid || true)"
    if [[ -z "$pid" ]]; then info "안 떠 있다."; return 0; fi
    kill "$pid" && success "이슈판 내렸다 (pid $pid)"
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
        error "GLG 의 Emacs(user 소켓)가 응답하지 않는다. 사람이 띄우는 자리다."
        return 1
    fi
}

board_age() {
    [[ -f "$FORGE_DB" ]] || { error "forge DB 가 없다"; return 1; }
    local mt now hrs
    mt=$(stat -c %Y "$FORGE_DB"); now=$(date +%s)
    hrs=$(( (now - mt) / 3600 ))
    echo "  DB 갱신: $(date -d "@$mt" '+%Y-%m-%d %H:%M')  (${hrs}시간 전)"
    sqlite3 -cmd '.timeout 5000' "file:$FORGE_DB?mode=ro" \
        "select '  리포 '||count(distinct repository)||' · open '||sum(state='open')||' · 전체 '||count(*) from issue"
}

# ── 메뉴 ────────────────────────────────────────────────

show_menu() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}sorge${NC} — 대신 해주지 않고 앞서 간다"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "  ${YELLOW}순회${NC}"
    echo "    1) 판 세우기 (sweep — 빚·문서 미정·대상 밖)"
    echo "    2) 브리핑 전부 (형제에게 그대로 던질 블록)"
    echo "    3) 한 리포만 브리핑 (대상 밖도 답한다)"
    echo "    4) 빚 기준 바꿔 보기 (기본 15커밋)"
    echo ""
    echo -e "  ${YELLOW}이슈판 (Magit Forge 캐시 · GitHub)${NC}"
    echo "    b) 띄우기      → http://127.0.0.1:$BOARD_PORT"
    echo "    s) 상태"
    echo "    q) 내리기"
    echo "    a) DB 나이·규모"
    echo "    p) forge-pull (stale 이면만)"
    echo "    P) forge-pull 강제"
    echo ""
    echo -e "  ${YELLOW}대장${NC}"
    echo "    l) LEDGER.md 열기"
    echo "    n) NEXT.md 열기"
    echo ""
    echo "    0) 나가기"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

usage() {
    cat <<EOF
sorge — 돌봄의 순회

  ./run.sh                 메뉴
  ./run.sh sweep [인자…]   순회. 인자는 sweep.py 로 그대로 간다
  ./run.sh brief [리포]    브리핑 블록
  ./run.sh board           이슈판 띄우기
  ./run.sh board-stop      내리기
  ./run.sh board-status    상태
  ./run.sh age             DB 나이·규모
  ./run.sh pull [force]    forge-pull (정책은 doomemacs-config 소유)

판정은 LEDGER.md 가 든다. 이 스크립트는 손잡이일 뿐이다.
EOF
}

main() {
    if [[ $# -gt 0 ]]; then
        case "$1" in
            sweep)        shift; sweep_board "$@" ;;
            brief)        shift; sweep_brief "${1:-}" ;;
            board)        board_start ;;
            board-stop)   board_stop ;;
            board-status) board_status ;;
            age)          board_age ;;
            pull)         shift; board_pull "${1:-}" ;;
            -h|--help|help) usage ;;
            *)            error "모르는 명령: $1"; echo ""; usage; exit 1 ;;
        esac
        return
    fi

    while true; do
        show_menu
        read -rp "선택: " choice
        echo ""
        case $choice in
            1) sweep_board ;;
            2) sweep_brief ;;
            3) read -rp "리포 이름: " r; [[ -n "$r" ]] && sweep_brief "$r" ;;
            4) read -rp "빚 기준 커밋 수: " d; [[ -n "$d" ]] && sweep_board --debt "$d" ;;
            b) board_start ;;
            s) board_status || true ;;
            q) board_stop ;;
            a) board_age ;;
            p) board_pull ;;
            P) board_pull force ;;
            l) ${PAGER:-less} "$SORGE_DIR/LEDGER.md" ;;
            n) ${PAGER:-less} "$SORGE_DIR/NEXT.md" ;;
            0) info "나간다."; exit 0 ;;
            *) error "잘못된 선택" ;;
        esac
        echo ""
        read -rp "계속하려면 Enter…"
    done
}

main "$@"
