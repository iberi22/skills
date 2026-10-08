# Ad-hoc harnesses and staging traps

Depth for when a fleet member (or any standalone script) has no canonical test
command. Read this when you are about to write a harness, or when a guard that
should have caught something is passing anyway.

## Why an ad-hoc harness, and how to make it stick

The failure mode is not "no tests". It is writing a verification, running it,
reporting "verified", and deleting it — so the next session has no evidence, the
work gets redone, and the same "unverified" warning reappears. Verification that
does not survive the session did not happen.

**Where it lives.** Next to the code it verifies, in a directory that gets
versioned with it. Never in `tmp/`, a scratch/cache dir, or anywhere pruned on a
timer. Ship a one-line runner (`bash <dir>/verify.sh`) that sets the same env the
production caller uses and writes its log beside itself, so a later session
reproduces the result with one command and no context.

**How it is named.** "Ad-hoc, N ok, 0 FAIL" — never "suite green". There is a
real difference and a reader needs to know which one they have. State the gap
(no repo, no CI, no test command) in the same breath as the result.

**What it must cover.** The behaviour you changed, in the environment the caller
uses. A harness that only asserts file contents verifies your typing, not your
logic.

## Checks with teeth

A check verified only against real data passes even when it can never fail. Every
new check needs both directions:

- a **mutant** that must trip it, and
- a **clean** case that must **not** trip it.

**Redacting a fixture to "look safe" silently disarms the check.** If a fixture
holds a token-shaped string purely so a detector can be shown to fire, and you
"clean" it into a redacted placeholder, the detector no longer matches it and the
check passes for a reason unrelated to detection. The tell: a check that verifies
"the guard detects X" needs X present. Build such a fixture by concatenation
instead of deleting it.

**Define each predicate once, then call it with both inputs.** Same function,
dirty and clean — the invocation cannot differ between them, so a predicate that
does not distinguish the two fails loudly instead of drifting.

**Ban `eval` + globals in the harness's own meta-tests.** Reading an expression
back out of the source and evaluating it is how you get `not` applied to a
truthy string, or a fixture list placed in the wrong variable so `all([])` passes
trivially. Write the predicate as a real function and call it.

**Use AST, not text matching, when searching for a construct.** Searching for
`, True)` to find placeholder assertions collides with legitimate data tables of
`(value, expected_bool)` pairs. Walk the tree: a placeholder is a constant passed
as a call argument. Keep a companion check that the legitimate occurrences still
exist, so the detector cannot be "fixed" by deleting real data.

**Check the whole population, not one instance.** A hygiene rule applied to a
single job verifies that one job. The same rule across all jobs of that class is
the one that pays.

## git-index traps for pre-commit / staging guards

These are not environment quirks; they are how git behaves, and each one makes a
staged-content guard silently pass.

| Trap | Behaviour | Rule |
|---|---|---|
| `git add a b c` with one missing path | Aborts rc 128 and stages **nothing**; the guard then scans an empty set | One path per call, each behind its own existence test. Never hide stderr. |
| `git add <path> ':!dir/*'` | Does **not** de-index anything already tracked — `git add` only adds | De-index explicitly with `git rm -r --cached <path>`; a pathspec exclusion is not a de-index. |
| `git rm --cached .` | Does not empty the index; entries stay staged | Reset to a known commit before asserting "nothing staged". |
| `git add` on a file identical to HEAD | Stages nothing, so a diff-based assertion sees an empty diff | Mutate the file with distinct content before staging. |
| `git commit` in a temp repo | A `pre-commit` hook configured globally can run and leave the temp repo unusable | Pass `--no-verify`; `reset --soft` is pure git and safe. |
| `git rm --cached` on a path in the commit base | Re-introduces the identical blob, so a diff still lists it | Assert with `git status --porcelain` and check for no `A`/`M` staged entries. |

**Never stage the guard's own fixtures.** A detection fixture contains
token-shaped data by design; committing the harness makes the backup's own guard
fire on it. Exclude the harness directory, and de-index it before measuring the
real repo's staging — then restore that state in a `finally`, so an interrupted
run does not leave the user's index modified.

**Restore state in a `finally` whenever a verification mutates shared state.**
The index and the job registry are both user state. Use a temp clone for
filesystem experiments and `try/finally` for the real repo.

**Do not let your own verification tool create the mess it is checking for.**
A syntax check that writes a compiled artefact into a versioned directory
recreates that artefact every run; compile in memory instead. Same for caches
that respect a no-bytecode environment variable — verify the env actually
suppresses writing rather than assuming the variable covers the tool.

## Hygiene invariants worth checking in a job registry

Cheap, and each one corresponds to a real failure mode:

- every `no_agent` job still names an existing script (otherwise it cannot run);
- no `no_agent` job carries a `model`/`provider`/`skills` (inert today, a trap
  the day the flag is removed — especially when the provider has no credit);
- no `no_agent` job has a prompt but no script (the limbo: not an LLM job, not a
  script job — dead, yet visible and apparently alive);
- every LLM job has a non-empty prompt (without one it burns tokens doing
  nothing every tick);
- no enabled job is in `error`, and no `script`/`monitor_script` reference points
  at a deleted file.
