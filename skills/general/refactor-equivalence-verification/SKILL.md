---
name: refactor-equivalence-verification
description: "Use when refactoring a script, gate or pipeline. Prove the output is unchanged, and run the thing after editing it."
---

# Refactoring without breaking the evidence

A refactor is only finished when its output is proven identical. Refactoring and
verifying are the same task, not two tasks.

## Compare against the right reference

The reference must be run the same way the real thing runs. A script that
resolves its data directory from its own location produces completely different
output when copied to `/tmp` -- it finds no corpus and reports zero.

```bash
# wrong: the copy cannot find its input
python3 /tmp/old.py > before.txt        # scans 0 files

# right: put the reference where it can find its input
git show <sha>:scripts/audit.py > scripts/_ref.py
python3 scripts/_ref.py > before.txt
diff before.txt after.txt && echo "byte-identical"
rm scripts/_ref.py
```

A diff that fails because of a misplaced path tells you nothing about the code.

## Run it after every edit, not once at the end

During one refactor the script was left calling a function that no longer
existed. `py_compile` does not catch a missing name at module scope, `pnpm run
lint` is `eslint src/` and does not look at `scripts/`, and `npm run test` is
validate-secrets.sh. Nothing failed, because nothing ran it.

Three things catch it, and none is optional:
- run the script itself, which needs the data it reads;
- an editor LSP, which flagged the undefined name instantly;
- a check that covers the directory (`npm run test:scripts`).

## Kill dead code you create, immediately

Removing an import as "unused" and needing it back one commit later costs a
revert. After a refactor, grep for what you removed:
unused helpers, unused imports, a helper that now has no callers. Report the
before and after byte counts.

## When a fixture must fail on purpose

Build it from the letter, not from the final text. `malform: 'B]'` compared
against `ABCD[i]` is `B`, so the condition is never true, the fixture stays
well-formed, and the test insists it is not. Write `'B'` and let the builder add
the bracket.

Then assert WHICH rule fired, not just that the validator rejected. One shared
keyword across all cases lets a wrong rejection satisfy the right test -- a
wrong fix wearing a right one's name.

## Prove the new check has teeth

A check that only ever returns green proves nothing. Break something on purpose,
confirm it goes red and names the offending file, remove the breakage, confirm
green. Do this before committing a new gate.

## Small diffs

Keep a refactor free of behaviour changes. When the output changes, that is a
different commit with a different explanation.
