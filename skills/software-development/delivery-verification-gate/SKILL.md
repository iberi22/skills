---
name: delivery-verification-gate
description: 'Use when claiming something works: run the full gate.'
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Delivery Verification Gate

Never report something as working without executing this gate on the EXACT artifact being delivered. A single HTTP 200 or exit code is not proof.

## The false-green classes (measured, not hypothetical)

A check that passes for the WRONG reason is worse than one that fails: it looks
like protection and protects nothing. These four all occurred in one session, each
caught only by deliberately breaking the thing being tested.

1. **Substring matches against paths.** Asserting `"/lib" in output` to mean "broken
   lib path" passes for every healthy `/nix/store/.../lib` — the substring is inside
   the good value. Assert on the parsed value (`pathlib.Path(p).exists()`), never on
   a fragment of the string.
2. **A test that duplicates production logic.** Copying the classification under test
   into the test closure means the test passes even when the production call site is
   bypassed. Call the real function; if it is unreachable, extract it so it is
   reachable (`classify_health()` called by both handler and test).
3. **A fixture with a frozen clock.** A hardcoded timestamp in fake data drifts out of
   every staleness window, so an unrelated alert fires in all cases and MASKS the one
   under test. Two checks then pass for the wrong reason. Compute timestamps relative
   to `datetime.now()`.
4. **Testing a copy of the artifact under test.** Reimplementing a shell script's logic
   in Python proves the reimplementation, not the script. Execute the real artifact
   (`bash script.sh`) against a controllable fake dependency.

Corollary: clippy/tests do NOT catch dead-delegation. If a function is still called
from the tests, bypassing its production caller is invisible to both. For config-like
code that fails silently, add a source-level guard test that asserts the production
call site still exists — and state its limit (grep cannot catch logic smuggled into
the function body; review is still required).

## Rules

1. Verify on the exact branch/commit served: `git status -sb` + `git log --oneline -1` must match what you claim. Never switch branches under a running server — re-verify after every checkout.
2. Route matrix, not one URL: curl every user-facing route, assert status AND content (byte size sane, key marker present, no error-overlay strings). Example markers: `WebGL2RenderingContext`, `ReferenceError`, `Traceback`, `Application error`.
3. Server-log scan AFTER the requests: `grep -c ERROR <server.log>` must show zero NEW errors. Old log lines don't count — compare timestamps.
4. Run the repo gates that apply (unit, typecheck, build, e2e) and quote real output numbers (e.g. `39 passed`, `1013 pages`), never from memory of an earlier run on different code.
5. If any gate fails: fix, re-run the FULL gate (not just the failed part), and only then report. A delivery report always includes: branch/commit, gate outputs, route matrix, log scan result.
6. Long-lived dev servers: start them logging to a file (`> /tmp/<app>-dev.log 2>&1`), never piped through `tail` (it hides the log you must scan).
7. UI deliveries: the route matrix includes each theme and a touch viewport, with screenshots you actually looked
   at (contact sheets are fine). A capture of one flat color is a harness failure, not a pass — retry it
   (see `gentleman-playwright` → Hardening rules). Compile every template in the unit suite so a syntax error in
   a shared component fails the gate before any browser runs.
8. Test results are for one commit: quote its SHA. A QA report on an older worktree is not evidence for the tip.

## Data-derived UI: compute, never hardcode

When a page shows counts, totals or type breakdowns, derive them from the same
source the data pipeline uses. Measured 2026-10-01 on GOS: a landing page
documented relationships `CONTAINS` and `FITS` that did not exist in the graph
while omitting 14 that did, because the list was hand-written. Every number was
an approximation. Fixing it meant computing from `graph-data.json` at build
time so the page cannot drift from the data again.

**The edge key is not always `label`.** Check the actual serializer before
reading edges — GOS wrote the relation name under `type`, so `.label` silently
yielded an empty list and the page rendered nothing.

**If a build-time file is imported, verify it exists on disk.** An endpoint like
`/api/evidence.json` may be generated only at runtime; importing
`public/api/evidence.json` fails the build or yields `undefined`. When a page
needs the same data as an API, read the same source the API reads (content
collections, database) instead of importing a generated artifact.

**If the schema filters fields, the flag never arrives.** A `doi_status` key on
each study was read correctly by the code but discarded by the Zod schema
before reaching the runtime, because each study is a strict `z.object` and
`.passthrough()` only applies one level up. Symptom: the fix is applied, the
build succeeds, and the count does not move. Check the schema, not just the
consumer.

## Self-review before claiming done

After a fix, re-read your own diff looking for work that is now redundant or
contradicts the new state. Measured 2026-10-01: a commit moved three selectors
to a stronger color *before* fixing the global token those selectors read,
leaving a comment citing a hex value that no longer existed anywhere. A follow-up
commit reverting them removed 16 lines and made the change easier to review.

- Stale comments that cite now-superseded values are worse than no comment.
- Redundant local overrides hide the fix that actually worked.
- After a cleanup commit, re-run the audit that motivated the original change to
  prove behavior is identical (compare counts, not just exit codes).

## Pitfalls

- **Reporting success from a re-run without checking the diff.** A green gate
  on a tree with uncommitted changes is not a delivery.
- **Trusting `RC=0` for content.** Exit codes cover crashes, not wrong numbers.
  Assert the actual values the page will show.
- **Registering after writing.** The ledger must be populated from tool output,