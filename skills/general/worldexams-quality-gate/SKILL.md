---
name: worldexams-quality-gate
description: Use when validating or repairing generated WorldExams/SaberParaTodos bundle markdown before opening a PR. CJK/English leakage, evidenced ICFES axes, answer-letter rebalance, dual validators.
---

# WorldExams quality gate v2

Validates generated `questions_data/**/weekly/*-MASTERY-bundle.md` before it reaches a PR.
Calibrated against already-merged content: a gate that flags merged files is mis-specified, not the content.

## Two validators, both must pass

```bash
node scripts/validate-bundles-v52.mjs <file.md> [more.md ...]
node saberparatodos/scripts/validate_content.js --country=colombia --grade=<N>  # needs node_modules
```

WHERE EACH ONE ACTUALLY RUNS, verified 2026-10-01:

- `validate-bundles-v52.mjs` runs in **CI** (`.github/workflows/deploy-preview.yml`),
  on the changed bundle files. It is `npm run validate`.
- It does **NOT** run in `.husky/pre-commit`. The hook runs three things: the
  SWAL leak gate, `scripts/husky-guard.mjs --staged`, and the interlock that
  blocks unsafe generators. A bundle with bad feedback commits locally and is
  caught by CI, not by the hook.
- `validate_content.js` is a separate older validator under `saberparatodos/`.
  It is not wired into the hook or into `deploy-preview.yml`.

So a green `git commit` does not mean the content passed. Run the validator
yourself before pushing, or wait for CI.

`validate_content.js` needs `saberparatodos/node_modules`. In a fresh worktree, symlink it from the
main checkout, run, then delete the symlink. To validate files that only exist in a worktree, copy
them into the main checkout, run, then **delete the copies**.

## Defects the generator actually produces

| Defect | Detection | Fix |
|---|---|---|
| CJK injected into Spanish prose | `grep -nP '[\x{4e00}-\x{9fff}\x{3040}-\x{30ff}\x{ac00}-\x{d7af}]'` | rewrite the phrase in Spanish |
| Cyrillic/Greek in words | `grep -nP '[\x{0400}-\x{04ff}\x{0370}-\x{03ff}]'` | transliterate or rewrite |
| English words in Spanish prose (`signalling`, `el_noise`) | word list over slug-stripped text | replace with Spanish |
| Duplicated `**Contexto:**` line | count each field vs question count | drop the 2nd (mangled) copy |
| A question missing `**ICFES:**` | `ICFES count != question count` | restore the evidenced axis |
| Answer-letter bias (7/12 on B, or zero D) | repo validator warning | rebalance (below) |

**The CJK grep range in the cron spec is malformed**: `\x{ac00}-\xd7af` errors with
"range out of order in character class". The working endpoint is `\x{d7af}`.
Always confirm a detector detects: append real CJK to a temp copy and grep it.

## Accent check must skip slugs

Protocol requires ASCII kebab slugs and `**ID:**` values, so `el-realismo-magico` is CORRECT and
`Realismo Mágico` in prose is also correct. Strip slugs first, then look for the unaccented word:

```python
re.sub(r"[a-z0-9]+(?:-[a-z0-9]+)+", " ", line)   # remove slugs/ids
re.search(r"\b(magico|tambien|fisica|quimica|cancer|farmacos)\b", stripped)
```

Do NOT add real Spanish cognates to the English blocklist (`defender`, `correct`, `answer` are
valid Spanish and appear in merged content).

## ICFES axes must be evidenced

An axis is valid only if it already appears in >=3 merged bundles of the SAME subject. Compute the
set from the subject dir rather than guessing. For `lengua` the evidenced trio is:

- `Competencia Lectora (Literal)`
- `Competencia Lectora (Inferencial)`
- `Competencia Lectora (Crítica)`

Forbidden: the subject name as the axis, combined forms, and axes from another subject.

## Difficulty ranges

`validate_content.js` only requires each header be in the ALLOWED SET
`{D3-D4, D5-D6, D7-D8, D9-D10}` - it does NOT enforce a fixed distribution. A 3/3/4/2 split is
tolerated in merged content. Enforce monotonic (non-decreasing) progression as an error; treat
distribution drift as a warning only.

## Answer-letter rebalance

Rotate the correct option as a WHOLE LINE so its `<!-- feedback: -->` travels with it, then
relabel A)-D). Never rewrite option text. Target 3/3/3/3 in a 12-question bundle; move only from
over-represented letters to under-represented ones. Verify on a copy first: option text + feedback
sets must be identical per question before/after.

## Static packs

Never hand-edit packs. Regenerate from the markdown:

```bash
node saberparatodos/scripts/generate-static-packs.js --all-weekly --changed-only
```

`.husky/pre-push` calls `scripts/husky-guard.mjs --changed`, which regenerates the
changed packs itself and then calls `assertGeneratedPacksCommitted()`. So a
commit that leaves a pack unstaged is refused at push time, not at commit time.
After generating by hand, verify each pack's `correct_answer` matches the
markdown `[x]` letter and that every `options[].feedback` is populated.

## Commit hygiene

The pre-commit hook validates only STAGED bundles, so stage the verified subset explicitly rather
than `git add questions_data/`. A failing W31 in the tree must not block a good W27-W30 commit.

## Related

- [[hermes-cron-worldexams-pipeline]] - the 30-min autonomous tick
