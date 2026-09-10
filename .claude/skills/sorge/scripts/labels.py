#!/usr/bin/env python3
"""sorge labels — put the judgment on the thing it judges.

THE STANDARD
------------
Three axes, namespaced `ns:value`. Nothing else. A label is self-describing
wherever it is read, so the scheme survives a move to GitLab or Forgejo without
a translation table -- the forge only has to store strings.

    house:<repo>    whose lane is this          (many allowed)
    state:<value>   where in the lifecycle      (single-valued)
    ball:<who>      who must move next          (single-valued)

The GRAMMAR is inherited from forge-config's sweeper protocol, which already
proved it on live repos: `agent:ready|running|done|blocked`, set with `label-set`
so a lifecycle never accumulates two values (forge-config NEXT.md § "Use
`label-set` for lifecycle status; avoid accumulating"). The VOCABULARY is
deliberately different. There, `agent:done` means "first-review triage
completed". Here the lifecycle is the one in LOOP.md § mission:

    분류 → 착수 → 검수 → 제안 → 머지|폐기

Aliasing one onto the other would let two lanes read the same word two ways,
which is the failure this house names as its own ("같은 낱말이 두 뜻으로 굳는다").

WHAT HAS NO LABEL
-----------------
No label means UNCLASSIFIED, and that is the whole debt list. This is the axis
that used to be `verdict=재분류필요` in TRIAGE.md -- a value someone had to
write, and then rewrite every time the ledger moved. Absence needs no
maintenance and cannot go stale, so the board's debt count is now honest by
construction rather than by discipline.

Likewise `house:` is omitted where the issue's repo already answers it. In
`entwurf`, an issue is obviously entwurf's. The label earns its place only on
coordination issues -- filed in `sorge`, about somebody else's lane.

WHAT LABELS CANNOT HOLD
-----------------------
`done_when` (a re-runnable command), `impl=`, `defects=` -- strings, and no label
can carry a string. An earlier draft of this file said they "belong in issue
COMMENTS", which was incoherent with the very next paragraph: LOOP § never keeps
comments SHUT. Caught in cross-review (terra, 2026-09-10, P0-2) after the
migration had already run, so the board briefly promised a canonical home that
did not exist.

They live in the ATTEMPT WORKTREE -- `~/repos/wt/<house>/<issue>/NEXT--attempt-*`
-- and the house's own citizen writes them, which is also who reads them. sorge
writes nothing there and comments on nobody's issue.

`wt=` is not stored at all. That path is a CONVENTION, not a judgment, so it is
derivable, and deriving it is strictly better than storing it: a stored path can
agree with a worktree that was removed, which is precisely how LOOP's second gate
could read green against a directory that no longer existed. `board.py` derives
it and flags any `state:running|review|proposed` with no worktree on disk.

THE CONTRACT THIS TOUCHES
-------------------------
`LOOP.md § never` forbade "이슈에 코멘트·라벨·닫기 — 밖으로 나가는 쓰기 전부".
GLG amended it on 2026-09-10: labels open, comments and closing stay shut,
because the stated reason ("자동 답신은 남의 트리아지 용량을 갉는다") is a
property of comments -- they notify, they land in a stranger's inbox -- and not
of labels. The amendment is the CONTRACT's, not this script's: terra's review
was right that a docstring cannot reinterpret a contract, and it was written
before GLG's edit landed. Writes here are `label-set`, never comment or close.
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
TRIAGE = os.path.join(SORGE, "TRIAGE.md")
OWNER = "junghan0611"

# Lifecycle. Single-valued: an issue is in exactly one of these, or in none
# (= unclassified). Colours are muted on purpose -- the board is read in a
# terminal far more often than in the web UI.
STATES = [
    ("state:ready",    "0E8A16", "분류 끝 — 착수 가능"),
    ("state:running",  "1D76DB", "착수 — 워크트리/브랜치가 돈다"),
    ("state:review",   "5319E7", "검수 — 다른 학교 형제가 읽는 중"),
    ("state:proposed", "FBCA04", "제안 — GLG 머지 판단 대기"),
    ("state:blocked",  "B60205", "막힘 — 밖의 무엇을 기다린다"),
    ("state:parked",   "BFBFBF", "보류 — 필요하지만 지금은 아니다"),
]
# Who must move next. This replaces TRIAGE's `verdict` axis: 담당자몫 → ball:owner,
# GLG결정필요 → ball:glg. The two remaining verdicts were not judgments about the
# issue at all -- 보류 is a state, and 재분류필요 is the absence of one.
BALLS = [
    ("ball:owner", "C2E0C6", "공은 그 집 담당자에게"),
    ("ball:glg",   "D93F0B", "공은 GLG 에게 — 사람만 닫을 수 있다"),
    ("ball:sorge", "C5DEF5", "공은 sorge 에게 — 가리키고 넘길 몫"),
]
HOUSE_COLOR = "EDEDED"

# Repos to PRE-SEED `house:` into. A convenience, not the rule.
#
# The rule was wrong once and it is worth saying how, because the wrong version
# reads perfectly sensible: `house:` was gated on WHICH REPO HOLDS THE ISSUE
# (sorge, later also agent-config as the former coordination seat). But the
# question a `house:` label answers is not "where was this filed" -- it is "does
# this issue's work cross houses". Those come apart, and the agent-config
# caretaker hit the seam within an hour of the first use (2026-09-10): they read
# `andenken#13`/`#14`, judged part of the work theirs -- the skill surface,
# `memory-sync`/`semantic-memory`, lives in agent-config -- and then had nowhere
# to put that judgment, because `andenken` had no `house:` vocabulary. So the
# judgment evaporated and the next `--mine` call would offer the same two issues
# as fresh candidates forever.
#
# So the gate moved: `ensure_house()` creates the label lazily, in whatever repo
# turns out to hold a cross-house issue. The original principle survives intact
# -- do not label where the repo already answers the question -- while the wrong
# proxy for it is gone. Pre-seeding these two only saves a round-trip on the two
# repos where it is already known to be needed.
COORD_HOUSES = {"sorge", "agent-config"}


def sh(cmd, check=True):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.stderr.write(r.stderr)
    return r


def ledger_houses():
    out = []
    for line in open(LEDGER, encoding="utf-8"):
        m = re.match(r"^\|\s*([a-zA-Z0-9._-]+)\s*\|\s*배정\s*\|", line)
        if m:
            out.append(m.group(1))
    return out


def ensure(houses, dry):
    """Create the label definitions. Idempotent; never deletes.

    `house:` labels go only into COORD_HOUSES. Elsewhere the repo name already IS
    the house, so shipping thirteen redundant labels into every repo would be
    exactly the "묻지 않은 곳에 설치하는 것" this house forbids.
    """
    for repo in houses:
        want = list(STATES) + list(BALLS)
        if repo in COORD_HOUSES:
            want += [(f"house:{h}", HOUSE_COLOR, f"{h} 의 몫") for h in houses]
        have = set()
        r = sh(f"gh label list -R {OWNER}/{repo} --limit 100 --json name -q '.[].name'")
        if r.returncode == 0:
            have = set(r.stdout.split())
        todo = [w for w in want if w[0] not in have]
        print(f"  {repo:<18} 있음 {len(want)-len(todo):>2}/{len(want)}  만들 것 {len(todo)}")
        for name, color, desc in todo:
            if dry:
                print(f"      + {name}")
                continue
            sh(f'gh label create "{name}" -R {OWNER}/{repo} '
               f'--color {color} --description "{desc}" --force')


def ensure_house(repo, house, dry):
    """Create `house:<house>` in `repo` on demand, right before it is needed.

    Lazy on purpose. Pre-creating the whole vocabulary in all thirteen repos
    would put twelve labels nobody uses into every house -- the "묻지 않은 곳에
    설치하는 것" this house forbids -- while pre-creating in none loses judgments
    that were actually made. Creating it at the moment a judgment needs it is the
    only option that costs nothing and drops nothing.
    """
    name = f"house:{house}"
    r = sh(f"gh label list -R {OWNER}/{repo} --limit 100 --json name -q '.[].name'")
    if r.returncode == 0 and name in r.stdout.split():
        return
    print(f"      (라벨 신설: {repo} ← {name})")
    if not dry:
        sh(f'gh label create "{name}" -R {OWNER}/{repo} '
           f'--color {HOUSE_COLOR} --description "{house} 의 몫" --force')


def assign(spec, dry):
    """`<repo>#<n>=<house>[,<house>]` — record that this issue's work is theirs.

    This is the verb the candidate lane was missing. A caretaker reads a
    candidate, decides it is (partly) their share, and that decision has to land
    somewhere or the board will keep proposing it. It lands on the issue.
    """
    m = re.match(r"^([A-Za-z0-9._-]+)#(\d+)=(.+)$", spec)
    if not m:
        sys.exit(f"형식: <repo>#<번호>=<house>[,<house>]  받은 것: {spec}")
    repo, num, hs = m.group(1), m.group(2), [h.strip() for h in m.group(3).split(",")]
    known = ledger_houses()
    # The issue's OWN repo must be named too, once any house: label exists.
    # `classify()` reads `hs = labels or [repo]` -- the repo is a FALLBACK, so the
    # first house: label silently switches it off. Labelling only the newcomer
    # would therefore evict the owning house from its own issue, which is the
    # opposite of what the judgment said. Add it back automatically rather than
    # trusting every caller to remember an implementation detail.
    if repo in known and repo not in hs:
        hs.append(repo)
    for h in hs:
        if h not in known:
            sys.exit(f"대장에 없는 집이다: {h}  (대장 밖은 대상이 아니다)")
    print(f"  {repo}#{num} → " + ",".join(f"house:{h}" for h in hs))
    for h in hs:
        ensure_house(repo, h, dry)
    if dry:
        return
    sh(f"gh issue edit {num} -R {OWNER}/{repo} "
       + " ".join(f'--add-label "house:{h}"' for h in hs))


# ── TRIAGE.md 에 갇혀 있던 판정을 라벨로 옮긴다 ──────────────────────
# This runs ONCE. It is a migration, not a mode of operation: after it, the
# judgment lives on the issue and TRIAGE.md has nothing left to hold.
VERDICT_BALL = {"담당자몫": "ball:owner", "GLG결정필요": "ball:glg"}
STATE_MAP = {"착수": "state:running", "검수": "state:review",
             "제안": "state:proposed", "분류": "state:ready"}


def open_issues():
    """Only living issues get labels.

    A closed issue's judgment is history, and labelling it would put a live
    lifecycle value on something whose lifecycle already ended -- the board would
    then have to filter it back out, which is a marker maintaining a marker.
    """
    q = f"owner:{OWNER} is:issue is:open"
    r = sh("gh api graphql --paginate -f query='"
           "query($endCursor:String){search(query:\"" + q + "\",type:ISSUE,"
           "first:100,after:$endCursor){pageInfo{hasNextPage endCursor}"
           "nodes{...on Issue{number repository{name}}}}}' "
           "-q '.data.search.nodes[]|.repository.name+\"#\"+(.number|tostring)'")
    return set(r.stdout.split())


def triage_lines(ref):
    """The migration's input, which the migration itself deleted.

    Once TRIAGE.md became a pointer, `--migrate` read an empty file and reported
    zero -- a replay or a correction would have had to restore git history by
    hand. `--from-ref` names the commit the rows still live in, so the migration
    stays re-runnable after its own source is gone.
    """
    if ref:
        r = sh(f"git -C {SORGE} show {ref}:TRIAGE.md")
        if r.returncode != 0:
            sys.exit(f"ref 에서 TRIAGE.md 를 못 읽었다: {ref}")
        return r.stdout.splitlines()
    return open(TRIAGE, encoding="utf-8").read().splitlines()


def transition(spec, dry):
    """`<repo>#<n>=<state>[,<ball>]` — move an issue along its lifecycle.

    The verb that was missing. `label-set` semantics existed only inside
    `--migrate`, so every day-to-day transition fell back to a raw
    `gh issue edit --add-label` -- which cannot keep the single-value contract
    the whole board depends on. The author of that contract then used raw
    gh issue edit on sorge#17 within the hour, which is about as clear a
    demonstration as a missing verb can give (terra, 2026-09-10, 2차 P1).
    """
    m = re.match(r"^([A-Za-z0-9._-]+)#(\d+)=(.+)$", spec)
    if not m:
        sys.exit(f"형식: <repo>#<번호>=<state>[,<ball>]  받은 것: {spec}")
    repo, num = m.group(1), int(m.group(2))
    states = {n.split(":")[1] for n, _, _ in STATES}
    balls = {n.split(":")[1] for n, _, _ in BALLS}
    want = []
    for v in [x.strip() for x in m.group(3).split(",")]:
        if v in states:
            want.append(f"state:{v}")
        elif v in balls:
            want.append(f"ball:{v}")
        else:
            sys.exit(f"모르는 값: {v}\n  state: {' '.join(sorted(states))}"
                     f"\n  ball : {' '.join(sorted(balls))}")
    apply([(repo, num, want)], dry)


def plan(houses, ref=None):
    live = open_issues()
    rows = []
    for line in triage_lines(ref):
        m = re.match(r"^junghan0611/([a-zA-Z0-9._-]+)#(\d+)\t(.*)$", line.rstrip("\n"))
        if not m:
            continue
        repo, num, rec = m.group(1), int(m.group(2)), m.group(3)
        if f"{repo}#{num}" not in live:
            continue
        hm = re.search(r"house=([^\s(]+)", rec)
        hs = [h for h in (hm.group(1).split("·") if hm else [repo]) if h in houses]
        if not hs:
            continue  # 대상 밖 — 라벨을 붙이지 않는다. 세지도 묻지도 않는다.
        vm = re.search(r"verdict=([^\s(]+)", rec)
        sm = re.search(r"state=([^\s(]+)", rec)
        labels = []
        if vm and vm.group(1) in VERDICT_BALL:
            labels.append(VERDICT_BALL[vm.group(1)])
        # `보류` carried two different facts under one word, and only one of them
        # is a state. "보류(대상 아님)" meant the repo was outside the ledger --
        # so the moment GLG widens the ledger, that row is a stale lie while the
        # loop's gate still reads green (measured twice: 2026-09-08 for three
        # houses, 09-09 for andenken). Those rows get NO label on purpose: they
        # resurface as debt, which is the only honest answer. A real "보류" --
        # needed, but not now -- becomes `state:parked`.
        if "대상 아님" in rec:
            # This row's ONLY judgment was "outside the ledger", and the ledger
            # has since moved -- so there is no judgment left to carry. It gets
            # no state label at all (`house:` may still apply) and resurfaces as
            # debt. Mapping its `state=분류` would launder a dead verdict into a
            # live one, which is how the gate stayed green while the answer was
            # wrong (2026-09-08 three houses, 09-09 andenken).
            pass
        elif vm and vm.group(1) == "보류":
            labels.append("state:parked")
        elif sm and sm.group(1) in STATE_MAP:
            labels.append(STATE_MAP[sm.group(1)])
        if repo == "sorge":
            labels += [f"house:{h}" for h in hs]
        if labels:
            rows.append((repo, num, sorted(set(labels))))
    return rows


def apply(rows, dry):
    """Set, don't add.

    `state:` and `ball:` are contracted single-valued, and an --add-label-only
    writer cannot keep that promise: re-run after a correction and the issue
    carries both the old and the new value, with the board silently reading
    whichever the API returns first. So every write first REMOVES the other
    values in that namespace, making the operation idempotent and the invariant
    true by construction rather than by nobody having pressed it twice yet.
    This is forge-config's `label-set` rule ("avoid accumulating"), which sorge
    inherited in name and now actually implements.
    """
    for repo, num, labels in rows:
        want_ns = {l.split(":")[0] for l in labels if l.startswith(("state:", "ball:"))}
        cur = []
        r = sh(f"gh issue view {num} -R {OWNER}/{repo} --json labels "
               f"-q '.labels[].name'")
        if r.returncode == 0:
            cur = r.stdout.split()
        drop = [c for c in cur
                if c.split(":")[0] in want_ns and c not in labels]
        add = [l for l in labels if l not in cur]
        if not add and not drop:
            print(f"  {repo}#{num:<4} 이미 맞다")
            continue
        print(f"  {repo}#{num:<4} +{','.join(add) or '—'}"
              + (f"  -{','.join(drop)}" if drop else ""))
        if dry:
            continue
        args = " ".join(f'--add-label "{l}"' for l in add)
        args += " " + " ".join(f'--remove-label "{l}"' for l in drop)
        sh(f"gh issue edit {num} -R {OWNER}/{repo} {args}")


def main():
    ap = argparse.ArgumentParser(description="sorge 표준 라벨 — 정의와 이관")
    ap.add_argument("--ensure", action="store_true", help="라벨 정의를 만든다")
    ap.add_argument("--migrate", action="store_true", help="TRIAGE.md 판정을 라벨로")
    ap.add_argument("--from-ref", metavar="REF",
                    help="TRIAGE.md 를 이 커밋에서 읽는다 (포인터로 바뀐 뒤의 재실행)")
    ap.add_argument("--house", metavar="SPEC", action="append", default=[],
                    help="후보 판정을 굳힌다: <repo>#<번호>=<house>[,<house>]. "
                         "라벨이 없으면 그 리포에 신설한다. 여러 번 줄 수 있다")
    ap.add_argument("--set", metavar="SPEC", action="append", default=[],
                    help="생애 전이: <repo>#<번호>=<state>[,<ball>]. "
                         "같은 축의 기존 값을 지우고 새 값 하나를 쓴다(label-set)")
    ap.add_argument("--go", action="store_true", help="실제로 쓴다 (기본은 dry-run)")
    a = ap.parse_args()
    dry = not a.go
    houses = ledger_houses()
    if dry:
        print("── dry-run. 쓰려면 --go ──\n")
    if a.set:
        print(f"생애 전이 {len(a.set)}건\n")
        for spec in a.set:
            transition(spec, dry)
    if a.house:
        print(f"후보 판정 굳히기 {len(a.house)}건\n")
        for spec in a.house:
            assign(spec, dry)
    if a.ensure:
        print(f"라벨 정의 — 대장 {len(houses)}집\n")
        ensure(houses, dry)
    if a.migrate:
        rows = plan(houses, a.from_ref)
        print(f"\nTRIAGE.md → 라벨: {len(rows)}건\n")
        apply(rows, dry)
    if not (a.ensure or a.migrate or a.house or a.set):
        ap.print_help()


if __name__ == "__main__":
    main()
