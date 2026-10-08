---
name: worldexams-pipeline
description: "Use when generating, repairing or auditing WorldExams bundles. Real commands, real gates, and what a green result does not prove."
version: "2.0.0"
updated: "2026-10-01"
---

# WorldExams Pipeline

> Supersedes the v1 skill, which documented a JSON pipeline whose scripts were
> stubs (`generator.py` printed "we simulate the output structure" and returned
> placeholder data). The corpus is Markdown under `questions_data/`. These are
> the commands that exist.

## Where things are

- Corpus: `questions_data/<country>/<subject>/<grade>/<year>/weekly/*.md`
- Gates: `scripts/validate-bundles-v52.mjs`, `scripts/check-feedback-language.mjs`
- Gate fixtures: `npm run test:quality` (5 suites)
- Everything in one command: `npm run test:scripts`
- Interlock: `.husky/pre-commit` refuses the 16 unsafe Python generators
- Corpus census (reports, never enforces): `scripts/audit-difficulty-band.py`
- Triage lists: `docs/triage/<wave>/<list>.json`

## The standard

All four options of every question explain why they are right or wrong, in the
bundle's own language. No bare verdict (`Correcto`, `Try again`, `Revisa el
concepto`), no slot names as options, and no two wrong options sharing one
feedback string.

A short explanation is fine when it is real: a formula, a grammatical label, a
derivation. Judge by meaning, never by length.

## Repairing debt: triage before you delegate

1. Measure against `HEAD`, not against a stale base. A census taken from an old
   checkout is a phantom deficit.
2. Sort the findings: a valid question with thin feedback gets **repaired**; a
   false question with slot-named options gets **regenerated**. Repairing a
   placeholder just writes a good explanation about a question that does not
   exist.
3. Write the file list to `docs/triage/<wave>/<name>.json` and dispatch
   subagents from that list, so coverage is countable afterwards.
4. Verify independently. Do not accept a self-report. Re-run the gate over the
   exact file list, check the diff touches only the intended bundles, and read
   samples.

## Delegating repair waves

Give each subagent a self-contained brief: the file list, the rule it must
satisfy, and what it must not touch. Ask it to name what it changed and to flag
anything that made it pause.

What worked: one agent reported that two bundles were diagnosed as "missing
options" when the options were all present and three rows used `]` instead of
`)`. It corrected the brief rather than complying with it. **Check what a report
claims about the cause, not only the verdict.**

### Partitioning a queue across agents

Re-measure immediately before splitting, never reuse the original list: agents
started while you were counting, so the remainder is smaller than the head
number. Subtract the files an in-flight agent has already opened (grep its live
transcript for `questions_data/...`), then split the rest.

Verify the partition before dispatching, not after:

```python
a, b, c = (set(x["path"] for x in s) for s in slices)
assert len(a & b) == len(a & c) == len(b & c) == 0
assert len(a | b | c) == len(remainder)
```

Round-robin by index keeps lists balanced when one country dominates; grouping
by country or grade keeps each agent inside a coherent subject.

### Put each list in its own directory

The brief names a path the agent will read. Write the file exactly where the
brief says, then confirm it from disk before dispatching — a list written to
`docs/triage/wave-x/j1.json` while the brief says `docs/triage/wave-j1/j1.json`
sends three agents to report "list not found". `mv` the file if you got it
wrong; do not leave both copies.

### Pitfalls seen
- A subagent may edit a neighbouring bundle outside its list. Verify the diff.
- A worktree in which several agents and a cron job write at once will not merge
  cleanly. `git pull --rebase` fails by default. Preserve work by SHA, use an
  isolated worktree, verify overlap before touching anything.
- `git status` may show bundles another actor changed. `git restore --staged`
  them and commit only your own files.
- A push can be rejected mid-wave by a concurrent commit. Rebase, confirm the
  other actor's files survived by reading them, then push. If `develop`
  diverged because it holds your pre-rebase SHAs, diff their content against
  the rebased commits before forcing: identical content means the lease is safe.
- Do not run `pkill -f 'opencode run'` to free a stuck agent; it kills work.
- An agent that stops writing mid-file leaves a half-done bundle. Check its
  remaining files against the gate and hand any unfinished one to a fresh agent
  -- but first confirm it is in nobody else's list.

## Check prose you wrote before committing it

A long `write_file` can carry a stray CJK character, a truncated tail or a
duplicated paragraph that reads fine in the tool result. It reached a committed
doc once, in the middle of a Spanish sentence. After writing any non-trivial
document, scan it:

```bash
grep -nP '[\x{4e00}-\x{9fff}\x{3040}-\x{30ff}]' docs/FILE.md   # stray CJK
awk '{ if (length($0) > 100) print FILENAME":"NR": "length($0) }' docs/FILE.md  # runaway line
wc -c docs/FILE.md   # compare against what you wrote
```

A corpus is gated; your own documentation is not. Nothing else will catch this.

## Reading results honestly

- The validator prints errors on **stderr** and the summary on **stdout**.
  `grep ERROR` on stdout finds nothing even when the corpus is broken. Use the
  `quality:` line and the `Failures:` count.
- **A green gate is not a reviewed bundle.** It checks shape. It cannot tell a
  real question from a plausible one. Open samples and read them.
- A number without a second method is not a finding. An early scan reported
  "43 bundles with answer-key feedback" from the pattern `the key`; in those
  bundles "the key" means *the key points*, not *the answer key*. Recompute with
  a narrower pattern and an independent check before reporting anything.

## Adding a gate rule

Write the failing fixture first. Assert which rule fired, not just that the
validator rejected. Then run the whole corpus: a rule that fires on real bundles
is a finding, and pre-existing debt belongs in `KNOWN_BAD` in
`scripts/check-scripts.sh` (reported, not blocking).
