#!/usr/bin/env python3
"""sorge sweep — derive the cross-repo picture. Stores nothing.

Every fact here is re-derived on each run: note presence, commits-since-note,
self-mend skill presence. Only LEDGER.md holds anything, and only human
judgments. See AGENTS.md "대장의 유일한 규율".
"""
import argparse, os, re, subprocess, sys

HOME = os.path.expanduser("~")
REPOS = os.path.join(HOME, "repos", "gh")
BOTLOG = os.path.join(HOME, "repos", "gh", "notes", "content", "botlog")
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
    """Map repo-name -> (denote-id, lastmod). Derived from the §<repo> title convention."""
    out = {}
    if not os.path.isdir(BOTLOG):
        return out
    for f in sorted(os.listdir(BOTLOG)):
        if not f.endswith(".md"):
            continue
        head = open(os.path.join(BOTLOG, f), encoding="utf-8").read(2000)
        t = re.search(r'^title: "(.*)"', head, re.M)
        if not t:
            continue
        lm = re.search(r"^lastmod: (\S+)", head, re.M) or re.search(r"^date: (\S+)", head, re.M)
        stamp = lm.group(1)[:10] if lm else "0000-00-00"
        for tok in re.findall(r"§([A-Za-z0-9._-]+)", t.group(1)):
            k = tok.lower()
            if k not in out or stamp > out[k][1]:
                out[k] = (f[:-3], stamp, t.group(1))
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
            "ahead": ahead,
            "mend": os.path.isdir(os.path.join(repo, ".claude", "skills")),
            "judged": judged.get(name.lower(), set()),
        })
    return rows


def brief(r):
    """One dispatchable block -- hand this to that repo's caretaker as-is."""
    L = [f"### {r['repo']}", ""]
    if r["note"]:
        L.append(f"담당자 문서 `{r['note']}` — lastmod {r['note_lastmod']} 이후 **{r['ahead']}커밋**.")
        L.append("그 사이 무엇이 닫혔는지 노트가 모른다. 히스토리 한 줄과 필요한 헤딩만 덧댄다")
        L.append("(통째로 다시 쓰지 않는다 — Documents Grow, Not Get Edited).")
    else:
        L.append("담당자 문서가 **없다.** 없는 게 맞을 수도 있다 — 필요한지부터 판정한다.")
        L.append(f"마지막 커밋 {r['last']}. 필요하다고 판정되면 `botlog` 스킬로 만든다.")
    if not r["mend"]:
        L.append("")
        L.append("자기수선 스킬 없음. 반복되는 수선이 실제로 있는지만 보고, 없으면 만들지 않는다.")
    L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="sorge sweep")
    ap.add_argument("--brief", action="store_true", help="dispatchable per-repo blocks")
    ap.add_argument("--repo", help="one repo only")
    ap.add_argument("--debt", type=int, default=15, help="commits-since-note that counts as debt")
    a = ap.parse_args()

    rows = survey()
    if a.repo:
        rows = [r for r in rows if r["repo"] == a.repo]
        if not rows:
            print(f"no such repo under {REPOS}: {a.repo}", file=sys.stderr)
            return 2

    need = [r for r in rows if not r["note"] and not r["judged"] and r["last"] >= "2026-08-01"]
    settled = [r for r in rows if not r["note"] and r["judged"]]
    debt = sorted((r for r in rows if r["note"] and r["ahead"] >= a.debt),
                  key=lambda r: -r["ahead"])
    quiet = [r for r in rows if r["note"] and r["ahead"] < a.debt]

    if a.brief:
        for r in need + debt:
            print(brief(r))
        return 0

    print(f"# sorge sweep — {len(rows)} repos under {REPOS}\n")
    print(f"판정 필요 ({len(need)})   살아있는데 담당자 문서 없음 — 필요한지 GLG가 정한다")
    for r in need:
        print(f"    {r['repo']:24} 마지막 커밋 {r['last']}")
    print(f"\n빚 ({len(debt)})         리포가 노트보다 앞서 감")
    for r in debt:
        print(f"    {r['repo']:24} {r['ahead']:>4}커밋   {r['note']} ({r['note_lastmod']})")
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
