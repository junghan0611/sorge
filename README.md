# sorge

**This repository holds a name, a ledger, and almost no code. That is the point.**

`sorge` is where the agent siblings come to ask. It owns no product, ships no
binary, and does not run your build. What it keeps is the one thing a single
repository cannot keep for itself: **the view across all of them, and the memory
of what was already decided.**

## The name is the specification

From Heidegger, and already resident in the operator's garden:

| Term | Korean | What it means here |
|---|---|---|
| **Sorge** | 돌봄 · 마음씀 | care as the whole structure — the repo's namesake |
| **Besorgen** | 배려 | concern with *things* — caches, flakes, build files |
| **Fürsorge** | 심려 | solicitude toward *others* — the repo caretakers themselves |

`Fürsorge` splits in two, and the split **is** this repo's operating rule:

- **einspringende Fürsorge** — *leaping in.* You take over the other's task and
  do it for them. They become dependent and learn nothing.
- **vorausspringende Fürsorge** — *leaping ahead.* You run ahead, clear the view,
  and hand their own task back to them. They become free.

> **sorge never does the work. It leaps ahead and returns the work to whoever owns it.**

This is not decoration. It was learned the expensive way, before the name existed:
a 9.1 GB build cache was found by a central script that was about to delete it.
Deleting it would have been leaping in — and the note written that day says why
that fails: *"what someone else deleted, the caretaker will pile up again without
learning."* The operator stopped it and called the repo's own caretaker, who knew
which 60 MB was evidence and which 9 GB was regenerable. That is leaping ahead.

## What sorge carries

Four lanes, all of them the same act — go ahead, look, hand it back:

| Lane | sorge does | sorge never does |
|---|---|---|
| **Caretaker notes** (담당자 문서) | find which repos moved past their public note, and by how much | write the note for them |
| **Self-mend skills** | see which repos repeat a repair worth freezing into a repo-local skill | install one where the caretaker didn't ask |
| **Issues** | carry the cross-repo view no single tracker holds | close another repo's issue |
| **Stack precedent** | *"GraalVM native-image, not JVM — 7 repos already did this; the closest three are these"* | write your `flake.nix` |

The fourth lane exists because the operator kept saying it out loud. Opening a new
project meant explaining, again, to search the other repos for a similar `flake.nix`
or `run.sh`, and — for the hard cases like embedded targets or Clojure compiled
through GraalVM `native-image` — that landing on the JVM is *not* the intent. That
knowledge already lived in the repos. What was missing was a hand to fetch it.

## Memory, and why it does not rot

Two kinds, deliberately not in the same place:

- **The ledger** (`LEDGER.md`) — human judgments only. *"This repo needs no
  caretaker note, decided on this date."* Small, exact, permanent.
- **The chronicle** — the caretaker note for `sorge` itself, in the public garden.
  Prose, growing, semantically searchable. The repo that asks others to keep a
  note keeps its own first.

One discipline holds both: **anything derivable is never stored.** Whether a note
exists, how many commits a repo ran past it, whether a self-mend skill is present —
all of it is re-derived on every pass, never written down. A stored copy of a
derivable fact is a marker, and a marker has to be maintained; that proposal was
already made once here, and already refused for exactly that reason.

So the ledger holds only what no command can answer: *a decision.* Which is why a
pass that never runs cannot make it stale.

## Status

A vessel, early and deliberately thin. Care can turn out to be documentation, issue
triage, fixing a sibling's bug, or a template handed over at the right moment — the
shape is expected to grow into the name rather than the reverse.

Part of the operator's Heidegger axis: [`entwurf`](https://github.com/junghan0611/entwurf)
(Entwurf, projection) · [`geworfen`](https://github.com/junghan0611/geworfen)
(Geworfenheit, thrownness) · [`andenken`](https://github.com/junghan0611/andenken)
(Andenken, recollection) · **`sorge`** (Sorge, care).

## License

MIT
