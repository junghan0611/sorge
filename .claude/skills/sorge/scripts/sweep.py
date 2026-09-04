#!/usr/bin/env python3
"""sorge sweep — derive the cross-repo picture. Stores nothing.

Every fact here is re-derived on each run: note presence, commits-since-note,
self-mend skill presence. Only LEDGER.md holds anything, and only human
judgments. See AGENTS.md "대장의 유일한 규율".
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


def load_notes():
    """Map repo-name -> (denote-id, lastmod, title), read from the org SSOT.

    Two conventions, and they are different facts. A §<repo> token in the title
    means the note is ABOUT that repo. A `#담당자` token means the note IS that
    repo's caretaker document. A marked note always wins over an unmarked one --
    otherwise a topic note that merely mentions four repos would be mistaken for
    the caretaker doc of all four (measured 2026-09-04: it was).

    A trailing separator is stripped, so "§sorge #담당자", "§sorge:" and
    "§sorge-담당자" all name `sorge`.
    """
    out = {}
    if not os.path.isdir(BOTLOG):
        print(f"warn: {BOTLOG} not found -- every note will read as absent",
              file=sys.stderr)
        return out
    for f in sorted(os.listdir(BOTLOG)):
        if not f.endswith(".org"):
            continue
        head = open(os.path.join(BOTLOG, f), encoding="utf-8", errors="replace").read(2000)
        t = re.search(r"^#\+title:\s*(.+?)\s*$", head, re.M)
        if not t:
            continue
        ident = re.search(r"^#\+identifier:\s*(\S+)", head, re.M)
        # #+hugo_lastmod is GLG's hand-struck stamp meaning "I really revised this
        # document" -- not a publish concern despite the name. A 히스토리 line is a
        # log, not a revision, so it must NOT raise the baseline: doing that hid 246
        # commits of real debt on entwurf (measured and reverted 2026-09-04). The note
        # that reads as stale under this rule IS stale until its caretaker stamps it.
        lm = (re.search(r"^#\+hugo_lastmod:\s*\[(\d{4}-\d{2}-\d{2})", head, re.M)
              or re.search(r"^#\+date:\s*\[(\d{4}-\d{2}-\d{2})", head, re.M))
        stamp = lm.group(1) if lm else "0000-00-00"
        note_id = ident.group(1) if ident else f.split("--")[0]
        marked = "#담당자" in t.group(1)
        for tok in re.findall(r"§([A-Za-z0-9._-]+)", t.group(1)):
            k = tok.lower().rstrip("-._")
            if not k:
                continue
            cur = out.get(k)
            # marked beats unmarked; within the same class, newer wins
            if cur is None or (marked, stamp) > (cur[3], cur[1]):
                out[k] = (note_id, stamp, t.group(1), marked)
    return out


def load_ledger():
    """Repos already judged. Absence of a judgment is not a defect -- it is an open question."""
    judged = {}
    if not LEDGER:
        print("warn: LEDGER.md not found -- every judgment will read as open",
              file=sys.stderr)
        return judged
    for line in open(LEDGER, encoding="utf-8"):
        m = re.match(r"\|\s*([A-Za-z0-9._-]+)\s*\|\s*(불필요|보류|배정)\s*\|", line)
        if m:
            judged.setdefault(m.group(1).lower(), set()).add(m.group(2))
    return judged


def survey():
    notes, judged = load_notes(), load_ledger()
    rows = []
    for name in sorted(os.listdir(REPOS)):
        repo = os.path.join(REPOS, name)
        if not os.path.isdir(os.path.join(repo, ".git")):
            continue
        hit = notes.get(name.lower())
        ahead = 0
        if hit:
            c = git(repo, "rev-list", "--count", f"--since={hit[1]}", "HEAD")
            ahead = int(c) if c.isdigit() else 0
        rows.append({
            "repo": name,
            "last": git(repo, "log", "-1", "--format=%cs"),
            "note": hit[0] if hit else None,
            "note_lastmod": hit[1] if hit else None,
            "note_title": hit[2] if hit else None,
            "marked": hit[3] if hit else False,
            "ahead": ahead,
            "mend": os.path.isdir(os.path.join(repo, ".claude", "skills")),
            "judged": judged.get(name.lower(), set()),
        })
    return rows


def brief(r):
    """One dispatchable block -- hand this to that repo's caretaker as-is.

    Three things the receiving caretaker cannot derive and must not have to ask
    for: which note this is (a bare id is not recognizable), who sent it, and
    where the answer goes. A block missing those makes the receiver come back
    with questions, which is the sweep handing over its own work -- the exact
    inversion this house is named against.
    """
    L = [f"### {r['repo']}", ""]
    if r["note"]:
        kind = "담당자 문서" if r["marked"] else "§노트(#담당자 미표시)"
        L.append(f"{kind}: [[denote:{r['note']}][{r['note_title']}]]")
        L.append(f"마지막 갱신 {r['note_lastmod']} 이후 **{r['ahead']}커밋**. "
                 "그 사이 무엇이 닫혔는지 노트가 모른다.")
        L.append("`denotecli read <id> --outline` 으로 뼈대 먼저 — 통째로 읽고 다시 쓰지 않는다.")
        L.append("히스토리 한 줄 + 필요한 헤딩만 덧댄다 (Documents Grow, Not Get Edited).")
        L.append("쓰는 손은 `botlog` 스킬 — `agent-denote-add-history` / `agent-denote-add-heading`.")
    else:
        L.append("담당자 문서가 **없다.** 없는 게 맞을 수도 있다 — 필요한지부터 판정한다.")
        L.append(f"마지막 커밋 {r['last']}. 필요하다고 판정되면 `botlog` 스킬로 만든다.")
    if not r["mend"]:
        L.append("")
        L.append("자기수선 스킬 없음. 반복되는 수선이 실제로 있는지만 보고, 없으면 만들지 않는다.")
    L.append("")
    L.append(f"— `sorge` 순회 {datetime.date.today().isoformat()}. 대신 하지 않고 넘기는 것이다. "
             "판정도 갱신도 이 집 담당자 몫이고, 「불필요」라는 답도 답이다.")
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

    rows = survey()
    if a.repo:
        rows = [r for r in rows if r["repo"] == a.repo]
        if not rows:
            print(f"no such repo under {REPOS}: {a.repo}", file=sys.stderr)
            return 2

    cutoff = (datetime.date.today() - datetime.timedelta(days=a.recent_days)).isoformat()
    need = [r for r in rows if not r["note"] and not r["judged"] and r["last"] >= cutoff]
    settled = [r for r in rows if not r["note"] and r["judged"]]
    debt = sorted((r for r in rows if r["note"] and r["ahead"] >= a.debt),
                  key=lambda r: -r["ahead"])
    quiet = [r for r in rows if r["note"] and r["ahead"] < a.debt]

    if a.brief:
        for r in need + debt:
            print(brief(r))
        return 0

    print(f"# sorge sweep — {len(rows)} repos under {REPOS}\n")
    print(f"판정 필요 ({len(need)})   담당자 문서 없음 + 최근 {a.recent_days}일 내 커밋 — 필요한지 GLG가 정한다")
    for r in need:
        print(f"    {r['repo']:24} 마지막 커밋 {r['last']}")
    print(f"\n빚 ({len(debt)})         리포가 노트보다 앞서 감")
    for r in debt:
        tag = "담당자" if r["marked"] else "미표시"
        print(f"    {r['repo']:24} {r['ahead']:>4}커밋   {r['note']} ({r['note_lastmod']}) [{tag}]")
    unmarked = [r for r in rows if r["note"] and not r["marked"]]
    print(f"\n미표시 ({len(unmarked)})     §노트는 있으나 #담당자 표시가 없음 — 표시할지 GLG가 정한다")
    for r in unmarked:
        print(f"    {r['repo']:24} {r['note']}")
    print(f"\n판정됨 ({len(settled)})     대장에 박힘 — 다시 묻지 않는다")
    for r in settled:
        print(f"    {r['repo']:24} {'/'.join(sorted(r['judged']))}")
    print(f"\n조용함 ({len(quiet)})      노트가 리포를 따라잡고 있음")
    print("\n" + "-" * 60)
    print("파생 사실만 위에 있다. 저장된 것은 없다. 판정은 LEDGER.md 로.")
    print("다음: --brief 로 형제에게 그대로 건넬 블록을 뽑는다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
