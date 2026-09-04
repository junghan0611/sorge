#!/usr/bin/env python3
"""sorge sweep — derive the cross-repo picture from GLG's judgments.

The ledger holds the judgments: which repo is cared for, and WHICH NOTE is its
caretaker document (by denote id). Everything else is re-derived on every run --
that note's lastmod, commits since, self-mend skill presence. See AGENTS.md
"대장의 유일한 규율".

Why the note id is a judgment and not a derived fact: "which note is this repo's
caretaker document" is something only GLG decides. `§<repo>` in a title and the
`#담당자` marker are hints GLG leaves for human eyes, not a definition. Deriving
the judgment from those hints broke three different ways in one day (2026-09-04)
-- a stale export, a topic note mistaken for a caretaker doc, and a stamp that
the update procedure never raised. All three were the same error: treating a
judgment as derivable. A denote id is also the least perishable thing to store;
on that same day a caretaker note's title, slug, tags and filename all changed
while its identifier did not move.

So search still runs -- but it proposes, and the ledger decides.
"""
import argparse, datetime, os, re, subprocess, sys

HOME = os.path.expanduser("~")
REPOS = os.path.join(HOME, "repos", "gh")
# The org tree is the Denote SSOT. The exported md under notes/content lags it by
# an export cycle -- measured 2026-09-04, when a note renamed at 11:27 still carried
# its previous title in the export. Reading the export would make a fresh note look
# absent, which is the one wrong answer this tool must never give.
BOTLOG = os.path.join(HOME, "org", "botlog")


def _find_ledger():
    """Walk up to the repo root. A wrong path here would silently report every
    settled judgment as an open question -- the one failure this tool must not have."""
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        cand = os.path.join(d, "LEDGER.md")
        if os.path.isfile(cand):
            return cand
        d = os.path.dirname(d)
    return None


LEDGER = _find_ledger()


def git(repo, *args):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def index_notes():
    """Read every botlog note once. Returns (by_id, candidates).

    by_id:      denote id -> (lastmod, title, marked)
    candidates: repo token -> [denote id, ...] for notes whose title says §<token>

    `lastmod` is `#+hugo_lastmod` and nothing else. That field is GLG's
    hand-struck stamp meaning "I really revised this document"; a 히스토리 line
    is a log, not a revision, and must not raise it. Falling back to the newest
    history entry hid 246 commits of real debt on one repo (tried and reverted
    2026-09-04).

    `candidates` exists only to give an unjudged repo something to ask ABOUT.
    It never decides anything.
    """
    by_id, candidates = {}, {}
    if not os.path.isdir(BOTLOG):
        print(f"warn: {BOTLOG} not found -- every note will read as absent",
              file=sys.stderr)
        return by_id, candidates
    for f in sorted(os.listdir(BOTLOG)):
        if not f.endswith(".org"):
            continue
        head = open(os.path.join(BOTLOG, f), encoding="utf-8", errors="replace").read(2000)
        t = re.search(r"^#\+title:\s*(.+?)\s*$", head, re.M)
        if not t:
            continue
        title = t.group(1)
        ident = re.search(r"^#\+identifier:\s*(\S+)", head, re.M)
        note_id = ident.group(1) if ident else f.split("--")[0]
        lm = (re.search(r"^#\+hugo_lastmod:\s*\[(\d{4}-\d{2}-\d{2})", head, re.M)
              or re.search(r"^#\+date:\s*\[(\d{4}-\d{2}-\d{2})", head, re.M))
        by_id[note_id] = (lm.group(1) if lm else "0000-00-00", title, "#담당자" in title)
        for tok in re.findall(r"§([A-Za-z0-9._-]+)", title):
            k = tok.lower().rstrip("-._")
            if k:
                candidates.setdefault(k, []).append(note_id)
    return by_id, candidates


def load_ledger():
    """GLG's judgments: repo -> (판정, denote id or None).

    Absence of a judgment is not a defect -- it is a question nobody has asked
    GLG yet, and the sweep's job is to ask it with candidates in hand.
    """
    judged = {}
    if not LEDGER:
        print("warn: LEDGER.md not found -- every judgment will read as open",
              file=sys.stderr)
        return judged
    row = re.compile(r"^\|\s*([A-Za-z0-9._-]+)\s*\|\s*(배정|관리 안 함|보류|불필요)\s*\|\s*([^|]*)\|")
    for line in open(LEDGER, encoding="utf-8"):
        m = row.match(line)
        if not m:
            continue
        note = re.search(r"\b(\d{8}T\d{6})\b", m.group(3))
        judged[m.group(1).lower()] = (m.group(2), note.group(1) if note else None)
    return judged


def survey():
    by_id, candidates = index_notes()
    judged = load_ledger()
    rows = []
    for name in sorted(os.listdir(REPOS)):
        repo = os.path.join(REPOS, name)
        if not os.path.isdir(os.path.join(repo, ".git")):
            continue
        verdict, note = judged.get(name.lower(), (None, None))
        lastmod = title = None
        ahead = 0
        missing = False
        if note:
            hit = by_id.get(note)
            if hit:
                lastmod, title = hit[0], hit[1]
                c = git(repo, "rev-list", "--count", f"--since={lastmod}", "HEAD")
                ahead = int(c) if c.isdigit() else 0
            else:
                # The ledger names a note that is not in the org tree. Never
                # silently drop it -- a judgment pointing at nothing is the one
                # thing the ledger cannot self-heal.
                missing = True
        rows.append({
            "repo": name,
            "last": git(repo, "log", "-1", "--format=%cs"),
            "verdict": verdict,
            "note": note,
            "note_missing": missing,
            "note_lastmod": lastmod,
            "note_title": title,
            "ahead": ahead,
            "cands": [c for c in candidates.get(name.lower(), []) if c != note],
            "mend": os.path.isdir(os.path.join(repo, ".claude", "skills")),
        })
    return rows


def brief(r, by_id=None):
    """One dispatchable block -- hand this to that repo's caretaker as-is.

    Three things the receiving caretaker cannot derive and must not have to ask
    for: which note this is, who sent it, and where the answer goes. A block
    missing those makes the receiver come back with questions, which is the
    sweep handing over its own work -- the exact inversion this house is named
    against.
    """
    L = [f"### {r['repo']}", ""]
    if r["note"] and not r["note_missing"]:
        L.append(f"담당자 문서: [[denote:{r['note']}][{r['note_title']}]] — 대장에 박힌 정본.")
        L.append(f"마지막 도장 {r['note_lastmod']} 이후 **{r['ahead']}커밋**. "
                 "그 사이 무엇이 닫혔는지 노트가 모른다.")
        L.append("`denotecli read <id> --outline` 으로 뼈대 먼저 — 통째로 읽고 다시 쓰지 않는다.")
        L.append("히스토리 한 줄 + 필요한 헤딩만 덧댄다 (Documents Grow, Not Get Edited).")
        L.append("쓰는 손은 `botlog` 스킬 — `agent-denote-add-history` / `agent-denote-add-heading`.")
        L.append("**내용을 실제로 고쳤으면 `agent-denote-set-front-matter` 로 `:hugo_lastmod` 도장을 찍는다.** "
                 "히스토리 줄만 얹은 것은 수정이 아니고, 도장이 이 빚의 기준선이다.")
    elif r["note_missing"]:
        L.append(f"대장은 이 리포의 담당자 문서를 `{r['note']}` 로 지목하는데 "
                 f"`{BOTLOG}` 에 그 id가 없다.")
        L.append("**이건 담당자가 갚을 빚이 아니라 대장이 고쳐야 할 자리다.** GLG 확인이 필요하다.")
    else:
        L.append("**대장에 없다** — 이 리포를 돌볼지 GLG가 아직 정하지 않았다.")
        L.append(f"마지막 커밋 {r['last']}.")
        if r["cands"]:
            L.append("후보:")
            for c in r["cands"]:
                t = by_id.get(c, ("", "?", False))[1] if by_id else "?"
                L.append(f"  - `{c}` — {t}")
            L.append("이게 맞나 · 다른 노트인가 · 관리 안 하나?")
        else:
            L.append("제목에 `§` 로 이 리포를 언급하는 노트가 없다. "
                     "새로 만들 일인가 · 관리 안 할 일인가?")
    if not r["mend"]:
        L.append("")
        L.append("자기수선 스킬 없음. 반복되는 수선이 실제로 있는지만 보고, 없으면 만들지 않는다.")
    L.append("")
    L.append(f"— `sorge` 순회 {datetime.date.today().isoformat()}. 대신 하지 않고 넘기는 것이다. "
             "판정도 갱신도 이 집 담당자 몫이고, 「관리 안 함」이라는 답도 답이다.")
    L.append("결과는 GLG에게, 또는 `~/repos/gh/sorge/LEDGER.md` 에 판정으로.")
    L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="sorge sweep")
    ap.add_argument("--brief", action="store_true", help="dispatchable per-repo blocks")
    ap.add_argument("--repo", help="one repo only")
    ap.add_argument("--debt", type=int, default=15, help="commits-since-note that counts as debt")
    # 35 days reproduces the first sweep's window (2026-08-01, measured 2026-09-04),
    # so that measurement stays comparable. Widen it when GLG wants quieter repos judged.
    ap.add_argument("--recent-days", type=int, default=35,
                    help="a repo counts as alive if it committed within this many days")
    a = ap.parse_args()

    by_id, _ = index_notes()
    rows = survey()
    if a.repo:
        rows = [r for r in rows if r["repo"] == a.repo]
        if not rows:
            print(f"no such repo under {REPOS}: {a.repo}", file=sys.stderr)
            return 2

    cutoff = (datetime.date.today() - datetime.timedelta(days=a.recent_days)).isoformat()
    broken = [r for r in rows if r["note_missing"]]
    ask = [r for r in rows if not r["verdict"] and r["last"] >= cutoff]
    debt = sorted((r for r in rows if r["note"] and not r["note_missing"]
                   and r["ahead"] >= a.debt), key=lambda r: -r["ahead"])
    quiet = [r for r in rows if r["note"] and not r["note_missing"] and r["ahead"] < a.debt]
    silent = [r for r in rows if r["verdict"] and not r["note"]]
    dormant = [r for r in rows if not r["verdict"] and r["last"] < cutoff]

    if a.brief:
        for r in broken + ask + debt:
            print(brief(r, by_id))
        return 0

    print(f"# sorge sweep — {len(rows)} repos under {REPOS}\n")
    if broken:
        print(f"대장 고장 ({len(broken)})   대장이 가리키는 id가 org에 없다 — 담당자 아닌 대장의 일")
        for r in broken:
            print(f"    {r['repo']:24} {r['note']}")
        print()
    print(f"확인 요청 ({len(ask)})    대장에 없음 + 최근 {a.recent_days}일 내 커밋 — 후보를 들고 GLG에게 묻는다")
    for r in ask:
        c = ", ".join(r["cands"]) if r["cands"] else "후보 없음"
        print(f"    {r['repo']:24} 마지막 커밋 {r['last']}   후보: {c}")
    print(f"\n빚 ({len(debt)})         리포가 담당자 문서보다 앞서 감")
    for r in debt:
        print(f"    {r['repo']:24} {r['ahead']:>4}커밋   {r['note']} (도장 {r['note_lastmod']})")
    print(f"\n판정됨·문서 없음 ({len(silent)})  대장에 박힘 — 다시 묻지 않는다")
    for r in silent:
        print(f"    {r['repo']:24} {r['verdict']}")
    print(f"\n조용함 ({len(quiet)})      담당자 문서가 리포를 따라잡고 있음")
    print(f"잠잠함 ({len(dormant)})      대장에 없으나 {a.recent_days}일 내 커밋도 없음 — 아직 묻지 않는다")
    print("\n" + "-" * 60)
    print("대장이 든 것은 판정뿐이다: 리포 → 담당자 문서 denote id, 또는 관리 안 함.")
    print("나머지는 전부 여기서 다시 유도했고 저장된 것은 없다.")
    print("다음: --brief 로 형제에게 그대로 건넬 블록을 뽑는다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
