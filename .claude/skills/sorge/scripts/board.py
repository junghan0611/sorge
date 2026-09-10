#!/usr/bin/env python3
"""sorge board — the live cross-repo issue board, derived on every call.

WHY THIS EXISTS
---------------
`TRIAGE.md` used to hold this table. It rotted, twice, in four days: the ledger
grew and every row that said "not our target" became a lie without changing a
byte -- and the loop's `done_when` gate stayed green while the answer was wrong,
because the gate only asked "is this issue written down", never "is what is
written still true" (LOOP.md § done_when, measured 2026-09-08 and again 09-09).

A file cannot answer the second question. A command can, because it never
remembers -- it re-derives. So the state moved to where the issue already lives:
its LABELS. GLG, 2026-09-10: "상태는 어짜피 이슈에 있으니 이슈에 라벨과 상태를
적어놓고 누가되든 판보기 버튼을 누르면 그게 나오면 된다. 그렇게 되야 문서에
적느라 삽질을 안해 문서는 금방 썩어."

WHAT IS STILL A FILE, AND WHY
-----------------------------
`LEDGER.md` stays. It holds a judgment no command can answer -- which repos GLG
cares for, and which note is each one's caretaker document. That is the house
rule, not an exception to it (AGENTS.md § 대장의 유일한 규율): store judgments,
re-derive everything else. Labels are judgments too, but they are judgments that
live ON the thing they judge, so they cannot drift away from it.

THE ONE MEASUREMENT THAT SHAPED THIS
------------------------------------
Speed was never the problem. Measured 2026-09-10 on oracle:

    gh search issues --owner junghan0611 --state open --limit 200   2.08s
    gh api graphql  (85 issues + labels, one shot)                  1.45s

So there is no cache here, and there must not be one. A cache would be a second
copy of a fact GitHub already holds, on a machine that may not be the machine
you are reading from -- the exact shape this house forbids ("사본은 원문과
갈라진다"). The forge sqlite DB on this host is a separate, Emacs-owned lens
(`datasette/metadata.yml`); it reads the same GitHub, and it is not this tool's
source.
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SORGE = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LEDGER = os.path.join(SORGE, "LEDGER.md")

OWNER = "junghan0611"

# The three axes. Namespaced `ns:value` so a label is self-describing wherever it
# is read -- GitHub today, GitLab or Forgejo tomorrow. The shape is inherited
# from forge-config's sweeper protocol (`agent:ready|running|done|blocked`,
# single-valued via `label-set`), deliberately: that lane already proved the
# shape on live repos. The VALUES differ because the lifecycles differ -- there,
# `agent:done` means "first-review triage completed"; here the lifecycle is
# 분류 → 착수 → 검수 → 제안 → 머지|폐기. Same grammar, different vocabulary; do
# not alias one onto the other.
NS_HOUSE = "house:"   # whose lane is this. Only needed where issue repo != work repo.
NS_STATE = "state:"   # where in the lifecycle. Single-valued.
NS_BALL = "ball:"     # who must move next. Single-valued.

STATE_ORDER = ["blocked", "proposed", "review", "running", "ready", "parked"]
BALL_ORDER = ["glg", "owner", "sorge"]

WT = os.path.expanduser("~/repos/wt")

# LOOP's second gate: an issue claiming to be under way must have a worktree that
# actually exists. That gate used to compare against a `wt=` string somebody typed
# into TRIAGE.md -- but the path was never a judgment, it is a CONVENTION
# (`~/repos/wt/<house>/<issue>`), so it is derivable and must not be stored. The
# receipt that is NOT derivable -- done_when, who sat, what the review found --
# lives inside that worktree, written by the house's own citizen. sorge does not
# write it and does not comment on anybody's issue.
# `proposed` is deliberately NOT here, and the reason is a mistake worth keeping.
#
# LOOP's lifecycle is 분류 → 착수 → 검수 → 제안 → 머지, and I turned each arrow's
# name into a state value. But 제안 is an ACT sorge performs (sorge→GLG: "이 N개
# 머지합시다"), not a CONDITION an issue sits in. The agent-config caretaker
# labelled six issues `state:proposed` meaning "this is a proposal awaiting a
# decision" -- and that reading is the natural one for a coordination board. The
# gate then flagged all six as attempts with no worktree, which was the gate
# accusing them of a mistake that was mine.
#
# So `proposed` needs no worktree. Only 착수 and 검수 do, because only those two
# name work happening in a place. This is the very failure this house names --
# 같은 낱말이 두 뜻으로 굳는다 -- caught in the vocabulary I wrote to prevent it,
# an hour after writing it (terra 2차 + agent-config usage, 2026-09-10).
ATTEMPT_STATES = {"running", "review"}


def attempt(house, number):
    """(worktree exists, receipt file) for this issue's attempt, derived not stored."""
    d = os.path.join(WT, house, str(number))
    if not os.path.isdir(d):
        return False, None
    rc = next((f for f in sorted(os.listdir(d))
               if f.startswith("NEXT--attempt")), None)
    return True, (os.path.join(d, rc) if rc else None)


STATE_MARK = {
    "blocked": "■ 막힘",
    "proposed": "▲ 제안",
    "review": "◆ 검수",
    "running": "● 착수",
    "ready": "○ 분류됨",
    "parked": "· 보류",
}
BALL_MARK = {"glg": "GLG", "owner": "담당자", "sorge": "sorge"}


def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        sys.exit(r.returncode)
    return r.stdout


def ledger_houses():
    """Repos GLG has judged as cared-for. The ONLY thing this tool reads a file for.

    A repo absent here is not untriaged -- it is out of scope, and it is not
    counted, listed or asked about (AGENTS.md § 대상). That is why the debt
    number in this board can never grow just because GLG opened a new repo.
    """
    if not os.path.exists(LEDGER):
        return {}
    out = {}
    for line in open(LEDGER, encoding="utf-8"):
        m = re.match(r"^\|\s*([a-zA-Z0-9._-]+)\s*\|\s*(배정|관리 안 함)\s*\|", line)
        if m:
            out[m.group(1)] = m.group(2)
    return {k: v for k, v in out.items() if v == "배정"}


GQL = """
query($q: String!, $after: String) {
  search(query: $q, type: ISSUE, first: 100, after: $after) {
    pageInfo { hasNextPage endCursor }
    nodes { ... on Issue {
      number title url updatedAt
      repository { name }
      labels(first: 30) { nodes { name } }
      BODY
    } }
  }
}
"""


def fetch(query, body=False):
    """Ask for bodyText only when a caller must match against it.

    The candidate lane needs the body to apply word boundaries; the board does
    not, and pulling 86 bodies to render a table nobody reads them in would be
    payload for nothing.
    """
    gql = GQL.replace("BODY", "bodyText" if body else "")
    nodes, after = [], None
    while True:
        cmd = ["gh", "api", "graphql", "-f", f"query={gql}", "-F", f"q={query}"]
        if after:
            cmd += ["-F", f"after={after}"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            sys.stderr.write(r.stderr)
            sys.exit(r.returncode)
        s = json.loads(r.stdout)["data"]["search"]
        nodes += [n for n in s["nodes"] if n]
        if not s["pageInfo"]["hasNextPage"]:
            return nodes
        after = s["pageInfo"]["endCursor"]


def classify(node, houses):
    """Turn one issue's labels into the three axes, then join with the ledger.

    An issue with no `house:` label falls back to its own repo -- in `entwurf`
    the house is obviously entwurf, so labelling it there would be noise. The
    label earns its place only where the two differ, which in practice means
    coordination issues filed in `sorge` about somebody else's lane.
    """
    repo = node["repository"]["name"]
    labels = [l["name"] for l in node["labels"]["nodes"]]
    hs = [l[len(NS_HOUSE):] for l in labels if l.startswith(NS_HOUSE)] or [repo]
    # Both axes are contracted single-valued. Read them as LISTS anyway: a second
    # value is a real state of the world (two agents raced, or a `--set` was half
    # applied), and picking the API's first element would hide it behind a value
    # that looks perfectly normal. Reporting `ambiguous` is the honest failure.
    sv = [l[len(NS_STATE):] for l in labels if l.startswith(NS_STATE)]
    bv = [l[len(NS_BALL):] for l in labels if l.startswith(NS_BALL)]
    state = sv[0] if len(sv) == 1 else (None if not sv else "ambiguous")
    ball = bv[0] if len(bv) == 1 else (None if not bv else "ambiguous")
    target = any(h in houses for h in hs)
    wt_ok, receipt = (None, None)
    if state in ATTEMPT_STATES:
        # Check under every candidate house -- a coord issue filed in sorge has
        # its worktree under the house that does the work, not under sorge.
        for h in hs:
            wt_ok, receipt = attempt(h, node["number"])
            if wt_ok:
                break
    return {
        "repo": repo,
        "number": node["number"],
        "title": node["title"],
        "url": node["url"],
        "updated": node["updatedAt"][:10],
        "houses": hs,
        "state": state,
        "ball": ball,
        "target": target,
        # Unclassified is not a value you write down -- it is the ABSENCE of a
        # judgment, so it can never go stale. This is the row that used to be
        # `verdict=재분류필요` in TRIAGE.md, kept alive by hand.
        "unclassified": target and state is None,
        "wt": wt_ok,
        "receipt": receipt,
        "ambiguous": "ambiguous" in (state, ball),
        "body": node.get("bodyText", ""),
        "other": [l for l in labels
                  if not l.startswith((NS_HOUSE, NS_STATE, NS_BALL))],
    }


def here():
    """Which house am I sitting in? Derived from the git remote, never asked.

    GLG's phrasing was a BUTTON -- "누가되든 판보기 버튼을 누르면 그게 나온다".
    Making a caretaker type their own repo name turns the button back into a
    query, and it is the one fact the cwd already knows. Falls back to None so
    the caller can ask rather than guess wrong (agent-config caretaker, 2026-09-10).
    """
    r = subprocess.run("git remote get-url origin", shell=True,
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    m = re.search(r"[:/]([^/]+?)(?:\.git)?\s*$", r.stdout.strip())
    return m.group(1) if m else None


def mine(repo, houses):
    """What is this house's share -- including what was filed somewhere else.

    This is the question a caretaker cannot answer from inside their own repo,
    and it is the reason this house exists (AGENTS.md § 이 집이 있는 이유): a
    finding arrives across the system and leaves across it too, so the issue that
    names your repo is very often not filed in it.

    Two layers, and they are not the same kind of claim:

      확정  a `house:<repo>` label, or the issue simply lives in that repo.
            Someone judged it. This is the share.
      후보  the repo's NAME appears in some other house's open issue. Nobody
            judged anything; full-text search proposed it.

    Keeping them apart is the ledger rule applied one level down -- "서치는
    제안하고, 대장이 결정한다". Collapsing them would turn a grep hit into an
    assignment, which is how a caretaker ends up owning work nobody gave them.
    """
    owned = [r for r in (classify(n, houses) for n in
                         fetch(f"owner:{OWNER} is:issue is:open"))
             if repo in r["houses"]]
    hits = fetch(f'owner:{OWNER} is:issue is:open "{repo}" in:title,body', body=True)
    seen = {(r["repo"], r["number"]) for r in owned}
    # GitHub full-text matches substrings, so `agent-config` also hits
    # `edgeagent-config` -- measured as a live false positive by the agent-config
    # caretaker (2026-09-10), 1 of 9 candidates, an issue about an a2a SDK survey
    # with nothing to do with that house. A repo name is a word, so require word
    # boundaries. Only the CANDIDATE lane needs this; the 확정 lane is label- and
    # repo-based and cannot pick up a substring.
    word = re.compile(rf"(?<![\w-]){re.escape(repo)}(?![\w-])")
    cand = [c for c in (classify(n, houses) for n in hits)
            if (c["repo"], c["number"]) not in seen and repo not in c["houses"]
            and word.search(c["title"] + " " + (c.get("body") or ""))]

    print(f"━━ {repo} 의 몫 ━━\n")
    if owned:
        print(f"확정 {len(owned)} — 라벨이 붙었거나 이 집 이슈다")
        for r in sorted(owned, key=lambda r: (r["state"] or "~", r["number"])):
            mark = STATE_MARK.get(r["state"], "□ 미분류")
            ball = BALL_MARK.get(r["ball"], "—")
            print(f"    {mark:<8} 공={ball:<4} {r['repo']}#{r['number']:<4} {r['title'][:58]}")
        print()
    if cand:
        print(f"후보 {len(cand)} — 남의 집 이슈가 「{repo}」 를 이름으로 부른다.")
        print(f"     판정이 아니다. 읽고 「내 몫이다/아니다」를 네가 정한다.")
        for c in sorted(cand, key=lambda c: c["updated"]):
            print(f"    {c['repo']}#{c['number']:<4} {c['updated']}  {c['title'][:58]}")
        print()
    if not owned and not cand:
        print("아무것도 없다. 「없음」은 결함이 아니다.\n")


def render(rows, houses, show_out=False, total=None):
    tgt = [r for r in rows if r["target"]]
    out = [r for r in rows if not r["target"]]
    debt = [r for r in tgt if r["unclassified"]]

    # Say "선택" when a filter cut the rows. Printing a filtered count under the
    # word `open` made the header assert something false about the whole board --
    # the same class of error this house keeps naming ("한 표면에서 참인 것을 전
    # 표면의 완료로 보고").
    head = (f"선택 {len(rows)}/{total}" if total is not None and total != len(rows)
            else f"open {len(rows)}")
    print(f"━━ sorge 이슈판 · {head} · 대상 {len(tgt)} · 대상 밖 {len(out)} "
          f"· 미분류 {len(debt)} ━━\n")

    amb = [r for r in tgt if r["ambiguous"]]
    if amb:
        print(f"⚠ 단일값 위반 {len(amb)} — state/ball 이 둘 이상이다. label-set 으로 고쳐라")
        for r in amb:
            print(f"    {r['repo']}#{r['number']}")
        print()

    # LOOP § done_when, second gate. A stored `wt=` string could agree with a
    # worktree that no longer exists; a derived check cannot.
    ghost = [r for r in tgt if r["state"] in ATTEMPT_STATES and not r["wt"]]
    if ghost:
        print(f"⚠ 워크트리 없는 attempt {len(ghost)} — state 는 진행이라는데 "
              f"~/repos/wt 에 자리가 없다")
        for r in ghost:
            print(f"    {r['repo']}#{r['number']:<4} state:{r['state']}  {r['title'][:52]}")
        print()

    # A directory is not a receipt. Checking only that the worktree exists let the
    # gate read green on doomemacs-config#11 -- worktree present, NEXT--attempt-*
    # absent, and its done_when/impl/defects still only in `git show
    # 49ca747:TRIAGE.md` (terra, 2026-09-10, 2차 P1). The contract says the
    # receipt is the attempt's canonical record, so its absence is exactly as
    # loud as a missing worktree.
    bare = [r for r in tgt
            if r["state"] in ATTEMPT_STATES and r["wt"] and not r["receipt"]]
    if bare:
        print(f"⚠ receipt 없는 attempt {len(bare)} — 워크트리는 있는데 "
              f"NEXT--attempt-* 가 없다 (그 집 시민이 쓴다)")
        for r in bare:
            print(f"    {r['repo']}#{r['number']:<4} state:{r['state']}  {r['title'][:52]}")
        print()

    # And the same check in reverse, which nothing was doing. A worktree with no
    # lifecycle label is just as unexplained as a label with no worktree, but it
    # hides better: the issue shows up in the debt list, which reads as "nobody
    # has classified this yet" rather than "somebody is already working on it".
    # entwurf#110 was exactly that -- ~/repos/wt/entwurf/110 on branch
    # fix/110-second-checkout, labels [] (terra, 2026-09-10, 2차 P1).
    orphan = []
    for r in tgt:
        if r["state"] in ATTEMPT_STATES:
            continue
        for h in r["houses"]:
            if attempt(h, r["number"])[0]:
                orphan.append((r, h))
                break
    if orphan:
        print(f"⚠ 라벨 없는 워크트리 {len(orphan)} — 자리는 있는데 state 가 없다. "
              f"진행인가 잔해인가는 그 집이 판정한다")
        for r, h in orphan:
            print(f"    {r['repo']}#{r['number']:<4} ~/repos/wt/{h}/{r['number']}"
                  f"  {r['title'][:44]}")
        print()

    if debt:
        print(f"■ 미분류 {len(debt)} — 라벨이 없다. 이게 유일한 빚이다.")
        for r in sorted(debt, key=lambda r: r["updated"]):
            print(f"    {r['repo']}#{r['number']:<4} {r['updated']}  {r['title'][:66]}")
        print()

    by_house = {}
    for r in tgt:
        if r["unclassified"]:
            continue
        for h in r["houses"]:
            if h in houses:
                by_house.setdefault(h, []).append(r)

    for h in sorted(by_house):
        rs = by_house[h]
        print(f"▸ {h}  ({len(rs)})")
        rs.sort(key=lambda r: (STATE_ORDER.index(r["state"])
                               if r["state"] in STATE_ORDER else 99, r["number"]))
        for r in rs:
            mark = STATE_MARK.get(r["state"], f"? {r['state']}")
            ball = BALL_MARK.get(r["ball"], "—")
            tag = f"  [{','.join(r['other'])}]" if r["other"] else ""
            src = f"{r['repo']}#{r['number']}"
            print(f"    {mark:<8} 공={ball:<4} {src:<22} {r['title'][:52]}{tag}")
        print()

    if show_out:
        print(f"── 대상 밖 {len(out)} (대장에 없는 집 — 세지도 묻지도 않는다)")
        agg = {}
        for r in out:
            agg[r["repo"]] = agg.get(r["repo"], 0) + 1
        print("   " + " · ".join(f"{k} {v}" for k, v in
                                 sorted(agg.items(), key=lambda kv: -kv[1])))
        print()

    stuck = [r for r in tgt if r["ball"] == "glg"]
    if stuck:
        print(f"▲ 공이 GLG 에게 있는 것 {len(stuck)} — 이게 안 움직이면 레인이 선다")
        for r in stuck:
            print(f"    {r['repo']}#{r['number']:<4} {r['title'][:66]}")


def main():
    ap = argparse.ArgumentParser(
        description="sorge 이슈판 — 대장 join 된 라이브 표. 저장하지 않는다.")
    ap.add_argument("--debt", action="store_true", help="미분류만")
    ap.add_argument("--house", help="한 집만")
    ap.add_argument("--mine", metavar="REPO", nargs="?", const="",
                    help="그 집 담당자의 시야 — 확정된 몫 + 이름으로 불린 후보. "
                         "인자를 빼면 cwd 의 git remote 에서 유추한다")
    ap.add_argument("--all", action="store_true", help="대상 밖도 보인다")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    houses = ledger_houses()
    if a.mine is not None:
        target = a.mine or here()
        if not target:
            sys.exit("여기가 어느 집인지 못 읽었다 (git remote 없음). "
                     "이름을 대라: --mine <repo>")
        mine(target, houses)
        return
    rows = [classify(n, houses) for n in fetch(f"owner:{OWNER} is:issue is:open")]
    total = len(rows)
    if a.house:
        rows = [r for r in rows if a.house in r["houses"]]
    if a.debt:
        rows = [r for r in rows if r["unclassified"]]

    if a.json:
        json.dump({"houses": sorted(houses), "issues": rows},
                  sys.stdout, ensure_ascii=False, indent=2)
        print()
        return
    render(rows, houses, show_out=a.all, total=total)


if __name__ == "__main__":
    main()
