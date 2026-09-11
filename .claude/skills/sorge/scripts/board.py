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
import urllib.parse

# The skill is reached through symlinks -- six harness surfaces plus agent-config
# all point here, and `abspath` does not resolve them, so `..`x4 walked out of a
# stranger's directory and the ledger silently vanished. Measured 2026-09-10:
# abspath landed correctly from 1 of 8 call paths, realpath from 8 of 8.
# realpath resolves the link FIRST, so the root is the real repo no matter which
# door the caller came through.
HERE = os.path.dirname(os.path.realpath(__file__))
SORGE = os.path.realpath(os.path.join(HERE, "..", "..", "..", ".."))
LEDGER = os.path.join(SORGE, "LEDGER.md")

OWNER = "junghan0611"

# The five axes. Namespaced `ns:value` so a label is self-describing wherever it
# is read -- GitHub today, GitLab or Forgejo tomorrow. `priority:` is sorge's
# record of GLG's whole-board order, never a heuristic: absent means no order has
# been made, not the fourth quadrant. `brief:steward-ready` is sorge's attestation
# that the caretaker's live issue thread holds a concrete execution brief. The
# autonomous loop reads these judgments; it never manufactures either one from a
# title or body.
NS_HOUSE = "house:"       # whose lane is this. Only needed where issue repo != work repo.
NS_STATE = "state:"       # where in the lifecycle. Single-valued.
NS_BALL = "ball:"         # who must move next. Single-valued.
NS_PRIORITY = "priority:" # sorge's record of GLG's quadrant. Single-valued.
NS_BRIEF = "brief:"       # sorge's caretaker-brief attestation. Single-valued.
SINGLETON_PREFIXES = (NS_STATE, NS_BALL, NS_PRIORITY, NS_BRIEF)

STATE_ORDER = ["blocked", "proposed", "review", "running", "ready", "parked"]
BALL_ORDER = ["glg", "owner", "sorge"]
PRIORITY_ORDER = [
    "important-urgent",
    "important-not-urgent",
    "not-important-urgent",
    "not-important-not-urgent",
]
PRIORITY_MARK = {
    "important-urgent": "중긴",
    "important-not-urgent": "중안",
    "not-important-urgent": "안긴",
    "not-important-not-urgent": "안안",
}
BRIEF_READY = "steward-ready"

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
    # An unreadable ledger must NEVER render as an empty one. The docstring above
    # says an absent repo is out of scope -- so a missing FILE would put the whole
    # universe out of scope and print `미분류 0`, i.e. "you owe nothing". That is
    # the same failure `ad500ee` fixed on the issue axis (nobody-looked and
    # somebody-is-on-it rendering alike): the wrong answer is the reassuring one.
    # Loud and empty-handed beats quiet and confidently wrong.
    if not os.path.exists(LEDGER):
        sys.exit(f"LEDGER.md 를 못 읽었다: {LEDGER}\n"
                 f"  대장 없이는 「대상」을 가를 수 없고, 빈 대장은 「빚 0」 으로 보인다.\n"
                 f"  이 스크립트는 sorge 리포 안에서 해석돼야 한다 (지금 뿌리: {SORGE}).")
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
    } }
  }
}
"""


def fetch(query):
    """No issue BODY is ever requested, and that is now structural.

    This used to take `body=True` for the one caller that matched the repo name
    against issue text. GLG retired that axis on 2026-09-10 ("라벨에 리포이름을
    넣자고했는데 텍스트로 검색하면 안된다"), so nothing here reads a body, and the
    option is gone rather than left idle: a switch with no caller is the next
    person's invitation to search text again.
    """
    gql = GQL
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
    """Turn one issue's labels into the five axes, then join with the ledger.

    The issue's own repo is always one house -- in `entwurf` the house is
    obviously entwurf, so a `house:entwurf` label would be noise. `house:` adds
    only the OTHER houses an issue crosses into. Keeping the own repo after the
    first cross-house label is essential: labels augment the issue's home; they
    do not replace it.
    """
    repo = node["repository"]["name"]
    labels = [l["name"] for l in node["labels"]["nodes"]]
    labelled = [l[len(NS_HOUSE):] for l in labels if l.startswith(NS_HOUSE)]
    hs = list(dict.fromkeys([repo] + labelled))
    # Both axes are contracted single-valued. Read them as LISTS anyway: a second
    # value is a real state of the world (two agents raced, or a `--set` was half
    # applied), and picking the API's first element would hide it behind a value
    # that looks perfectly normal. Reporting `ambiguous` is the honest failure.
    sv = [l[len(NS_STATE):] for l in labels if l.startswith(NS_STATE)]
    bv = [l[len(NS_BALL):] for l in labels if l.startswith(NS_BALL)]
    pv = [l[len(NS_PRIORITY):] for l in labels if l.startswith(NS_PRIORITY)]
    fv = [l[len(NS_BRIEF):] for l in labels if l.startswith(NS_BRIEF)]
    state = sv[0] if len(sv) == 1 else (None if not sv else "ambiguous")
    ball = bv[0] if len(bv) == 1 else (None if not bv else "ambiguous")
    priority = pv[0] if len(pv) == 1 else (None if not pv else "ambiguous")
    brief = fv[0] if len(fv) == 1 else (None if not fv else "ambiguous")
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
        # Houses that a `house:` LABEL actually names, without the own-repo seat
        # the reader adds. `--mine` needs the difference: a gh label filter can
        # only see what is written, so quoting `houses` at the caller would
        # promise a number the filter does not return.
        "labelled_houses": labelled,
        "state": state,
        "ball": ball,
        "priority": priority,
        "brief": brief,
        "target": target,
        # Unclassified is not a value you write down -- it is the ABSENCE of a
        # judgment, so it can never go stale. This is the row that used to be
        # `verdict=재분류필요` in TRIAGE.md, kept alive by hand.
        "unclassified": target and state is None,
        "wt": wt_ok,
        "receipt": receipt,
        "ambiguous": "ambiguous" in (state, ball, priority, brief),
        "other": [l for l in labels if not l.startswith((NS_HOUSE,) + SINGLETON_PREFIXES)],
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

    ONE layer, and it is a judgment: a `house:<repo>` label, or the issue lives
    in that repo. Someone READ it and said so.

    There used to be a second lane -- 후보 -- where the repo's NAME appearing in
    some other house's open issue proposed a link. GLG retired the text axis on
    2026-09-10: *"내가 라벨에 리포이름을 넣자고했는데 텍스트로 검색하면 안된다."*
    The label WAS the instruction; the text lane was the older mechanism left
    standing beside it.

    It cannot be repaired, and the failures are not a tuning problem -- a repo
    name is an identifier we borrowed from ordinary words, and in a body it is
    just a word again. Measured 2026-09-10, with word boundaries already enforced:

      apply         `(apply fn args)` in elisp · `lens.apply` · the path
                    `apply/ax/ax.org`  -- an English verb and a function name
      junghan0611   `github.com/junghan0611/garden` -- it is the OWNER, so it is
                    inside every URL in every issue. Structurally 100% false
      garden        11 hits, 3 real -- a common word in GLG's own vocabulary
      org-20250624  the real repo name nobody writes; `org` finds nothing

    Three fixes were tried in one day and each uncovered the next: boundaries
    (`edgeagent-config`) -> vocabulary (`garden`) -> suffix (`org-20250624`).
    Across 13 houses the lane proposed 50 links.

    WHAT REPLACES THE DISCOVERY, because removing it must not remove the reason
    this house exists (AGENTS.md § 이 집이 있는 이유 -- a finding arrives across
    the system and leaves across it too, so the issue naming your repo is often
    not filed in it):

      발견   the BOARD's 미분류 lane -- what this code counts as debt.
      판정   `--house <repo>#<n>=<house>` writes what the reading found.
      몫     그 담당자가 여기서 확정으로 받는다.

    `house:` is a cross-house judgment, not a lifecycle state. The contract and
    code therefore agree: **only a missing `state:` is unclassified**. A row may
    name another house and still need lifecycle classification; `sorge#12` was
    the receipt that forced this distinction (terra review, 2026-09-10).

    Measured the same day: 10 cross-filed issues carry a `house:` label naming a
    repo other than the one they live in, and ALL 10 arrive here through 확정.
    The chain is built and loaded; the text lane was a grep impersonating the
     순회. It was an impersonation, so it lived on the luck of a word.
    """
    owned = [r for r in (classify(n, houses) for n in
                         fetch(f"owner:{OWNER} is:issue is:open"))
             if repo in r["houses"]]
    print(f"━━ {repo} 의 몫 ━━\n")
    # THIRD instance of today's form, and the worst-worded of the three.
    # `board.py:130` could not tell "대장에 없다" from "대장을 못 읽었다"; `sweep.py`
    # warned on a stream nobody read. Here a repo that is OUT OF SCOPE rendered
    # identically to a target house with nothing to do -- down to the closing
    # line "「없음」은 결함이 아니다", which does not merely stay silent but
    # actively reassures. A caretaker whose house GLG never registered was told
    # they were all caught up.
    #
    # It was also what made the retired 후보 lane look loudest exactly here: that
    # lane subtracted 확정, and an out-of-scope house has no 확정 to subtract, so
    # every full-text hit survived (garden: 11 proposed, 3 real). The noise and
    # the silence were ONE fault, which is why saying 밖 was half of its cure and
    # GLG retiring the text axis was the other half.
    #
    # The dirname is printed because it is DERIVED, not stored. GLG named the
    # real shape -- a house's human name need not be its repo name (`~/org` is
    # `org-20250624`, `~/repos/gh/notes` is `garden`). No alias column: a stored
    # alias is a marker, and this house refuses markers (`.diskclean-owned`,
    # 2026-08-10). Showing both names lets the caller pick the registered one.
    if repo not in houses:
        # Only when we are actually SITTING in that repo does the directory name
        # say anything. With an explicit `--mine <name>` the cwd is unrelated, and
        # printing its basename there invents a divergence that does not exist.
        cwd_name = os.path.basename(os.path.realpath(os.getcwd()))
        alias = (f" · 디렉터리 이름은 「{cwd_name}」"
                 if here() == repo and cwd_name != repo else "")
        print(f"⚠ 이 집은 대장에 없다 — 대상 밖이라 「확정」을 계산하지 않는다.")
        print(f"   remote 가 말하는 이름은 「{repo}」{alias}.")
        print(f"   대장에 다른 이름으로 올라 있으면 그 이름으로 불러라: --mine <이름>")
        # "판정 대기다" told the caretaker to wait and named no hand. This house's
        # own rule is to show the next move instead of the prohibition, and this
        # was the one line missing it (agent-config caretaker, user-seat review).
        print(f"   대상이 맞다고 보면 GLG 에게 대장 편입을 요청해라 — "
              f"대상은 GLG 가 요청할 때만 넓어진다.\n")
    if owned:
        print(f"확정 {len(owned)} — 라벨이 붙었거나 이 집 이슈다")
        for r in sorted(owned, key=lambda r: (r["state"] or "~", r["number"])):
            mark = STATE_MARK.get(r["state"], "□ 미분류")
            ball = BALL_MARK.get(r["ball"], "—")
            print(f"    {mark:<8} 공={ball:<4} {r['repo']}#{r['number']:<4} {r['title'][:58]}")
        print()
    if not owned:
        # Only a TARGET house may be told its emptiness is fine. Saying it to an
        # unregistered house is the reassurance the block above just warned about.
        if repo in houses:
            print("확정된 몫이 없다. 「없음」은 결함이 아니다.\n")
        else:
            print("확정이 없다. 「없음」이 아니라 「밖」이다 — 위 줄을 읽어라.\n")
    # Name where the UNJUDGED cross-house work lives, so that retiring the text
    # lane reads as a relocation and not as a loss. A caretaker must not conclude
    # from a short 확정 list that nothing out there concerns them -- that would be
    # today's silence fault a fourth time, one layer out.
    if repo in houses:
        # GLG's own description of the workflow this label axis exists for
        # (2026-09-10): "내가 apply 담당자면, 라벨 필터를 apply로 내놓고 뒤져보면,
        # A 리포에 apply 라벨이슈가 있으면 내것이구나 하면서 들여다 볼 수 있거든.
        # 즉, 내 판이 아니어도 내가 관심 가지고 보는거야."
        #
        # The lane above combines this filter with unlabeled issues in the
        # caretaker's own repo. This hands over the filter itself, because
        # 뒤져보다 is not the same act as 조회하다 -- one is a table somebody
        # rendered, the other is you moving around in it. A caretaker who can
        # only ask through this script cannot browse; a URL and a gh line let
        # them look without us, and let them show GLG what they saw.
        ql = urllib.parse.quote_plus(f'owner:{OWNER} is:issue is:open label:"house:{repo}"')
        # Say the number the filter returns, not just the filter. The lane above
        # counts 확정, which includes this house's OWN issues -- and those carry no
        # `house:` label at all (`LOOP.md:56`: 붙이는 것은 이슈 리포 ≠ 일하는 집일
        # 때만). So a caretaker reading 확정 20 and then getting 7 from the filter
        # meets a 13-issue gap that is contract, not loss. Today's whole commit is
        # about two situations that render alike; this is the mirror -- ONE
        # situation rendering as two numbers -- and it is closed the same way, by
        # saying which is which (agent-config caretaker, user-seat review).
        n_lab = len([r for r in owned if repo in r["labelled_houses"]])
        print(f"이 이름표를 어느 리포에서든 하나로 뒤진다 — **남의 판에 있는 {n_lab}건**:")
        print(f'     gh search issues --owner {OWNER} --state open --label "house:{repo}"')
        print(f"     https://github.com/search?q={ql}&type=issues")
        print(f"     (이 집 리포의 이슈는 라벨을 안 달므로 여기 안 나온다 — LOOP.md:56)")
        print()
        print("아직 판정 안 된 횡단 일은 위에 없다 — 판의 미분류 레인에 있고 sorge 가 읽는다:")
        print("     ./run.sh board --debt        (판정 전)")
        print("     ./run.sh label --house <repo>#<n>=<이 집>   (읽은 것을 적는다)")


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
        print(f"⚠ 단일값 위반 {len(amb)} — state/ball/priority/brief 가 둘 이상이다. label-set 으로 고쳐라")
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
        print(f"■ 미분류 {len(debt)} — lifecycle 라벨이 없다. 이게 유일한 분류 빚이다.")
        for r in sorted(debt, key=lambda r: r["updated"]):
            print(f"    {r['repo']}#{r['number']:<4} {r['updated']}  {r['title'][:66]}")
        print()

    # A ready owner issue is NOT autonomous work merely because it sounds small.
    # It needs both sorge's explicit GLG-priority record and sorge's verified
    # caretaker brief; absence is a stop signal, never an invitation for the loop
    # to infer intent.
    unready = [r for r in tgt if r["state"] == "ready" and r["ball"] == "owner"
               and (r["priority"] not in PRIORITY_ORDER or r["brief"] != BRIEF_READY)]
    if unready:
        print(f"⚠ 자율 착수 보류 {len(unready)} — sorge 우선순위 정리 또는 담당자 실행 지침 확인이 없다")
        for r in sorted(unready, key=lambda r: (r["repo"], r["number"])):
            missing = []
            if r["priority"] not in PRIORITY_ORDER:
                missing.append("sorge priority")
            if r["brief"] != BRIEF_READY:
                missing.append("sorge brief 확인")
            print(f"    {r['repo']}#{r['number']:<4} {' · '.join(missing):<22} {r['title'][:48]}")
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
        rs.sort(key=lambda r: (PRIORITY_ORDER.index(r["priority"])
                               if r["priority"] in PRIORITY_ORDER else 99,
                               STATE_ORDER.index(r["state"])
                               if r["state"] in STATE_ORDER else 99, r["number"]))
        for r in rs:
            mark = STATE_MARK.get(r["state"], f"? {r['state']}")
            ball = BALL_MARK.get(r["ball"], "—")
            priority = PRIORITY_MARK.get(r["priority"], "미정")
            brief = "✓" if r["brief"] == BRIEF_READY else "—"
            tag = f"  [{','.join(r['other'])}]" if r["other"] else ""
            src = f"{r['repo']}#{r['number']}"
            print(f"    {mark:<8} 우={priority:<2} 지침={brief} 공={ball:<4} {src:<22} {r['title'][:52]}{tag}")
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
                    help="그 집 담당자의 시야 — 확정된 몫만. "
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
