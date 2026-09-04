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
import argparse, datetime, json, os, re, subprocess, sys

HOME = os.path.expanduser("~")
REPOS = os.path.join(HOME, "repos", "gh")
# Notes come through `denotecli`, which reads the org tree -- the Denote SSOT.
# The exported md under notes/content lags it by an export cycle (measured
# 2026-09-04, when a note renamed at 11:27 still carried its previous title in
# the export), and reading the export would make a fresh note look absent, which
# is the one wrong answer this tool must never give. Going through denotecli
# rather than the directory keeps that rule in ONE place instead of two.


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
    """Ask denotecli for the botlog notes. Returns (by_id, candidates).

    by_id:      denote id -> (lastmod, title, marked)
    candidates: repo token -> [denote id, ...] for notes whose title says §<token>

    `lastmod` is `#+hugo_lastmod` and nothing else. That field is GLG's
    hand-struck stamp meaning "I really revised this document"; a 히스토리 line
    is a log, not a revision, and must not raise it. Falling back to the newest
    history entry hid 246 commits of real debt on one repo (tried and reverted
    2026-09-04).

    This used to open every .org under ~/org/botlog and regex the stamp out,
    because `denotecli` did not expose it. That parallel parser was a copy of a
    derivable fact -- the exact fault this house spent 2026-09-04 naming -- and
    it went wrong the way copies do: it read the date and dropped the clock, so
    a commit made earlier on the stamping day counted as debt (zotero-config
    measured it: commit 18:32 vs stamp 21:55). GLG had denotecli carry the stamp
    and the abstract that same day (`3c57689`), so the copy is retired here.
    Verified before switching: 8/8 stamps identical to what the regex produced.

    `candidates` exists only to give an unjudged repo something to ask ABOUT.
    It never decides anything.
    """
    by_id, candidates = {}, {}
    out = subprocess.run(
        ["denotecli", "search", "§", "--tags", "botlog", "--max", "999"],
        capture_output=True, text=True)
    if out.returncode != 0:
        print(f"warn: denotecli search failed -- every note will read as absent\n{out.stderr}",
              file=sys.stderr)
        return by_id, candidates
    try:
        notes = json.loads(out.stdout)
    except json.JSONDecodeError as e:
        print(f"warn: denotecli returned non-JSON: {e}", file=sys.stderr)
        return by_id, candidates

    for n in notes:
        _absorb(by_id, candidates, n)
    return by_id, candidates


def _absorb(by_id, candidates, n):
    """Fold one denotecli note record into the two indexes."""
    # `header_title` is the org `#+title:` in BOTH commands. `title` is not the
    # same key twice: `read` returns the front matter there, but `search` returns
    # the filename slug ("§denotecli-담당자-day-query-…"). Reading `title` would
    # hand a sibling a slug instead of a title and would break the `#담당자`
    # marker check, since the slug drops the `#`. Measured 2026-09-04.
    title = n.get("header_title") or n.get("title") or ""
    note_id = n.get("id")
    if not note_id:
        return
    # denotecli hands the org timestamp back verbatim: "[2026-09-04 Fri 15:02]".
    # Keep the clock -- `--since=<date>` means 00:00, so a stamp with no time
    # stays at 00:00 on purpose. That over-reports debt, and over-reporting is
    # the safe direction: reading something that exists as absent is the error
    # this house cannot afford.
    raw = n.get("hugo_lastmod") or n.get("date") or ""
    m = re.match(r"\[(\d{4}-\d{2}-\d{2})[^\]]*?(\d{2}:\d{2})?\]", raw)
    stamp = (f"{m.group(1)} {m.group(2)}" if m and m.group(2)
             else (m.group(1) if m else "0000-00-00"))
    by_id[note_id] = (stamp, title, "#담당자" in title)
    for tok in re.findall(r"§([A-Za-z0-9._-]+)", title):
        k = tok.lower().rstrip("-._")
        if k:
            candidates.setdefault(k, []).append(note_id)


def note_by_id(note_id):
    """One note the search may not have returned -- the ledger can name any id.

    The ledger holds a judgment, and a judgment is not required to live in a
    note whose title carries §. So a ledger id that the § search misses is not
    a broken ledger; it is a note titled differently. Ask for it by name.
    """
    out = subprocess.run(["denotecli", "read", note_id, "--outline"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return None


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
    row = re.compile(r"^\|\s*([A-Za-z0-9._-]+)\s*\|\s*(배정|관리 안 함|보류|불필요)"
                     r"\s*\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|")
    for line in open(LEDGER, encoding="utf-8"):
        m = row.match(line)
        if not m:
            continue
        note = re.search(r"\b(\d{8}T\d{6})\b", m.group(3))
        # A 곁노트 clause is a judgment the receiving caretaker cannot derive --
        # "this one is the 왜 layer", "this one is retired, read it as reference
        # only". Carried verbatim rather than parsed: the sentence is the payload,
        # and slicing a labelled clause costs nothing to maintain, whereas giving
        # the ledger a structured column would be a marker to keep alive.
        # It runs to the end of the cell, so the ledger writes it last. Ending it
        # at the first period once truncated "폐기 문서다. 참고만 하고" to just
        # "폐기 문서다" -- dropping the half that told the caretaker what to do.
        aside = re.search(r"곁노트:\s*(.*)$", m.group(5))
        judged[m.group(1).lower()] = (m.group(2), note.group(1) if note else None,
                                      aside.group(1).strip() if aside else None)
    return judged


def survey():
    by_id, candidates = index_notes()
    judged = load_ledger()
    rows = []
    for name in sorted(os.listdir(REPOS)):
        repo = os.path.join(REPOS, name)
        if not os.path.isdir(os.path.join(repo, ".git")):
            continue
        verdict, note, aside = judged.get(name.lower(), (None, None, None))
        lastmod = title = None
        ahead = 0
        missing = False
        if note:
            hit = by_id.get(note)
            if not hit:
                # The § search proposes; the ledger decides. A judgment may name
                # a note whose title carries no §, and that is not a broken
                # ledger -- it is a note titled differently. Ask by id before
                # calling it missing, or the tool reports the ledger as broken
                # for exercising exactly the freedom the ledger exists to hold.
                d = note_by_id(note)
                if d:
                    # Candidates go to a throwaway: a note fetched by id was
                    # named by the ledger, so it is already decided and has no
                    # business proposing itself anywhere.
                    _absorb(by_id, {}, d)
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
            "aside": aside,
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
        if r["ahead"]:
            L.append(f"마지막 도장 {r['note_lastmod']} 이후 **{r['ahead']}커밋**. "
                     "그 사이 무엇이 닫혔는지 노트가 모른다.")
            L.append("`denotecli read <id> --outline` 으로 뼈대 먼저 — 통째로 읽고 다시 쓰지 않는다.")
            L.append("히스토리 한 줄 + 필요한 헤딩만 덧댄다 (Documents Grow, Not Get Edited).")
            L.append("쓰는 손은 `botlog` 스킬 — `agent-denote-add-history` / `agent-denote-add-heading`.")
            L.append("**내용을 실제로 고쳤으면 `agent-denote-set-front-matter` 로 `:hugo_lastmod` 도장을 찍는다.** "
                     "히스토리 줄만 얹은 것은 수정이 아니고, 도장이 이 빚의 기준선이다.")
        else:
            # Reached only when GLG named this repo: a quiet repo is never raised
            # on its own. Saying "the note does not know what closed since" here
            # would be manufacturing a debt that the count just said is zero.
            L.append(f"마지막 도장 {r['note_lastmod']} 이후 **0커밋 — 노트가 리포를 따라잡고 있다.**")
            L.append("갱신할 빚이 없다. 지명받아 나온 블록이므로, 물을 것이 따로 있으면 그것만 묻는다.")
    elif r["note_missing"]:
        L.append(f"대장은 이 리포의 담당자 문서를 `{r['note']}` 로 지목하는데 "
                 "`denotecli` 가 그 id를 모른다.")
        L.append("**이건 담당자가 갚을 빚이 아니라 대장이 고쳐야 할 자리다.** GLG 확인이 필요하다.")
    elif r["verdict"]:
        L.append(f"대장 판정은 `{r['verdict']}` 인데 담당자 문서 id가 아직 비어 있다.")
        L.append(f"마지막 커밋 {r['last']}.")
        if r["cands"]:
            L.append("후보:")
            for c in r["cands"]:
                t = by_id.get(c, ("", "?", False))[1] if by_id else "?"
                L.append(f"  - `{c}` — {t}")
            L.append("이게 정본인가 · 다른 노트인가 · 새로 쓸 일인가?")
        else:
            L.append("제목에 `§` 로 이 리포를 언급하는 노트가 없다. 새로 쓸 일인가?")
    else:
        # Reached only via --repo on an off-scope repo: GLG asked by name, and
        # a direct question is not the sweep widening itself.
        L.append("**대장에 없다 — 대상이 아니다.** 이름을 대고 물었으니 후보만 보인다.")
        L.append(f"마지막 커밋 {r['last']}.")
        for c in r["cands"]:
            t = by_id.get(c, ("", "?", False))[1] if by_id else "?"
            L.append(f"  - `{c}` — {t}")
        L.append("대상으로 올릴지는 GLG가 정한다. 순회가 먼저 꺼내지 않는다.")
    if r["aside"]:
        L.append("")
        L.append(f"**대장의 곁노트** — {r['aside']}")
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
    # There was a --recent-days window here, feeding a 확인 요청 lane that asked
    # about every repo committed to lately. GLG removed the premise on
    # 2026-09-04 -- scope grows only on request -- so recency no longer selects
    # anything and the flag went with the lane.  See AGENTS.md § 대상.
    a = ap.parse_args()

    by_id, _ = index_notes()
    rows = survey()
    if a.repo:
        rows = [r for r in rows if r["repo"] == a.repo]
        if not rows:
            print(f"no such repo under {REPOS}: {a.repo}", file=sys.stderr)
            return 2

    broken = [r for r in rows if r["note_missing"]]
    debt = sorted((r for r in rows if r["note"] and not r["note_missing"]
                   and r["ahead"] >= a.debt), key=lambda r: -r["ahead"])
    quiet = [r for r in rows if r["note"] and not r["note_missing"] and r["ahead"] < a.debt]
    silent = [r for r in rows if r["verdict"] and not r["note"]]
    offscope = [r for r in rows if not r["verdict"]]

    if a.brief:
        # Naming a repo is itself the request: brief it whatever lane it fell in,
        # including off-scope and 조용함. A bare sweep briefs only what it would
        # raise on its own -- briefing every target would be the sweep widening
        # its own scope, and briefing a quiet repo would be manufacturing work.
        for r in (rows if a.repo else broken + silent + debt):
            print(brief(r, by_id))
        return 0

    print(f"# sorge sweep — {len(rows)} repos under {REPOS}\n")
    if broken:
        print(f"대장 고장 ({len(broken)})   대장이 가리키는 id가 org에 없다 — 담당자 아닌 대장의 일")
        for r in broken:
            print(f"    {r['repo']:24} {r['note']}")
        print()
    print(f"빚 ({len(debt)})         리포가 담당자 문서보다 앞서 감")
    for r in debt:
        print(f"    {r['repo']:24} {r['ahead']:>4}커밋   {r['note']} (도장 {r['note_lastmod']})")
    print(f"\n문서 미정 ({len(silent)})   대상이나 담당자 문서 id가 비어 있다 — 후보를 들고 묻는다")
    for r in silent:
        c = ", ".join(r["cands"]) if r["cands"] else "후보 없음"
        print(f"    {r['repo']:24} {r['verdict']}   후보: {c}")
    print(f"\n조용함 ({len(quiet)})      담당자 문서가 리포를 따라잡고 있음")
    print(f"\n대상 밖 ({len(offscope)})     대장에 없다 = 대상이 아니다. 묻지 않는다")
    print("            넓히는 손은 GLG 하나다. 이름을 대고 물으면 --repo <name> 이 답한다.")
    print("\n" + "-" * 60)
    print("대장이 든 것은 판정뿐이다: 리포 → 담당자 문서 denote id.")
    print("나머지는 전부 여기서 다시 유도했고 저장된 것은 없다.")
    print("다음: --brief 로 형제에게 그대로 건넬 블록을 뽑는다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
