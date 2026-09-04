# sorge

**The place the siblings come to ask.**

`sorge` holds what no single repository can hold for itself: **the view across all
of them, and the memory of what was already decided.**

Today that is mostly documents — a ledger, a contract, a caretaker's note. What it
grows into is open. Care turns out to be many things: a note kept current, an issue
triaged, a sibling's bug fixed, a template handed over at the right moment. The
shape is expected to grow into the name rather than the other way round.

## Why it exists

Not because notes go stale. That is a symptom.

The operator ships a lot of open source, and the repos are one system even though
they are many repositories. So an insight rarely belongs to the repo where it was
found. Working through the memory-axis logic in one place upgrades the *operator* —
and then a flaw becomes visible in a different repo that was invisible the day
before, not because that repo changed, but because the person looking at it did.

**Describing that finding to the one repo does not finish it.** The realization
crossed the whole system on its way in, and it has to cross it again on the way
out. Until now there was nowhere for it to land: it got spoken into one
conversation with one caretaker, and the other fifty never heard it.

`sorge` is that landing place, and the hand that fans it back out.

## The name is the specification

From Heidegger, and already resident in the operator's garden:

| Term | Korean | What it means here |
|---|---|---|
| **Sorge** | 돌봄 · 마음씀 | care as the whole structure — the repo's namesake |
| **Besorgen** | 배려 | concern with *things* — caches, flakes, build files |
| **Fürsorge** | 심려 | solicitude toward *others* — the repo caretakers themselves |

`Fürsorge` splits in two, and the split **is** the operating rule:

- **einspringende Fürsorge** — *leaping in.* You take over the other's task and do
  it for them. They become dependent and learn nothing.
- **vorausspringende Fürsorge** — *leaping ahead.* You run ahead, clear the view,
  and hand their own task back to them. They become free.

> **sorge does not do the work. It leaps ahead and returns the work to whoever owns it.**

This was learned the expensive way, before the name existed. A 9.1 GB build cache
was found by a central script that was about to delete it — which would have been
leaping in, and the note written that day already says why that fails: *"what
someone else deleted, the caretaker will pile up again without learning."* The
operator stopped it and called that repo's own caretaker, who knew which 60 MB was
evidence and which 9 GB was regenerable. That is leaping ahead.

## What care looks like so far

| Lane | sorge does | sorge does not |
|---|---|---|
| **Cross-cutting findings** | hold a realization that touches many repos, and give each one its own version of the question | decide it for them |
| **Caretaker notes** (담당자 문서) | find which repos moved past their public note, and by how much | write the note for them |
| **Self-mend skills** | see which repos repeat a repair worth freezing into a repo-local skill | install one where the caretaker didn't ask |
| **Issues** | carry the cross-repo view no single tracker holds | close another repo's issue |
| **Stack precedent** | *"GraalVM native-image, not the JVM — seven repos already did this; the closest three are these"* | write your `flake.nix` |

The last lane exists because the operator kept saying it out loud. Opening a new
project meant explaining, again, to search the other repos for a similar
`flake.nix` or `run.sh` — and for the hard cases like embedded targets or Clojure
compiled through GraalVM `native-image`, that landing on the JVM is *not* the
intent. That knowledge already lived in the repos. What was missing was a hand to
fetch it.

## Memory, and why it does not rot

Two kinds, deliberately not in the same place:

- **The ledger** (`LEDGER.md`) — human judgments only. *"This repo needs no
  caretaker note, decided on this date."* Small, exact, permanent.
- **The chronicle** — sorge's own caretaker note in the public garden. Prose,
  growing, semantically searchable. The repo that asks others to keep a note keeps
  its own first.

One discipline holds both: **anything derivable is never stored.** Whether a note
exists, how many commits a repo ran past it, whether a self-mend skill is present —
re-derived on every pass, never written down. A stored copy of a derivable fact is
a marker, and a marker has to be maintained; that proposal was made here once and
refused for exactly that reason.

So the ledger holds only what no command can answer: *a decision.* Which is why a
pass that never runs cannot make it stale.

## Scope

The operator's **open-source** repositories (`~/repos/gh`). Company work has its
own private chief-of-staff and is not this house's concern.

Part of the Heidegger axis: [`entwurf`](https://github.com/junghan0611/entwurf)
(projection) · [`geworfen`](https://github.com/junghan0611/geworfen) (thrownness) ·
[`andenken`](https://github.com/junghan0611/andenken) (recollection) · **`sorge`** (care).

## License

MIT
