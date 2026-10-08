---
name: skill-invocation-audit
description: "Use when a skill names another skill, chains skills, or when a chained skill silently fails to load. Enforces explicit tool-call phrasing, two-calls-for-two-skills, and the user-invoked-is-unreachable rule."
---

# Skill invocation convention

Naming a skill in prose does **not** load it. A dependency is only real when it
is written as an instruction to call the tool. Upstream fixed six call sites for
this exact defect; treat it as an error class, not a one-off.

## Three classes

| Class | Form | Verdict |
|---|---|---|
| A | names a skill, no explicit tool call | **BROKEN**, may silently not load |
| B | `Call the Skill tool with "x"` | correct |
| C | points at a user-invoked skill as a tool call | **BROKEN**, unreachable |

## Rule 1: explicit tool call, always

```
WRONG  First run the brainstorming skill, then use systematic-debugging.
WRONG  See the `code-review` skill. Apply `github-auth` before pushing.
RIGHT  Call the Skill tool with "brainstorming".
RIGHT  Call the Skill tool with "code-review". Call the Skill tool with "github-auth".
```

Prose forms that do **not** trigger a load: `` `skill-name` ``, `/skill-name`,
"the X skill", "see X", "load X", "X handles this". Backticks are documentation,
not an instruction.

## Rule 2: two skills means two calls

Never pass two names to one call. A single call loads one skill.

```
WRONG  Call the Skill tool with "grilling" and "to-spec".
RIGHT  Call the Skill tool with "grilling". Then call the Skill tool with "to-spec".
```

Split into two sentences, two separate calls, so each load is independently
verifiable.

## Rule 3: a user-invoked skill is unreachable

A skill with `disable-model-invocation: true`, or
`policy.allow_implicit_invocation: false`, can **never** be reached by another
skill. No phrasing fixes this. The only valid form is an instruction to the human.

```
WRONG  Call the Skill tool with "setup-matt-pocock-skills". Then triage the issue.
RIGHT  Tell the user to run /setup-matt-pocock-skills, then wait for their reply.
```

If a step's precondition is a user-invoked skill, either rephrase it as an
instruction to the human, or delete the precondition and make the step
self-sufficient. Never leave a tool call aimed at one.

## Auditing a tree

```
python3 ~/.hermes/skills/_meta/check_skill_references.py \
    ~/.hermes/skills ~/.claude/skills --top 30
```

Reports class A, class C, and name collisions; exits non-zero on findings.
`--json` for machine output, `--quiet-class-b` to keep the console readable.

Interpret with care:

- A backticked name may be a path, a binary, or prose. `jules` is both a CLI
  and a skill name; most hits are the CLI.
- Fenced code blocks are skipped unless the line holds an explicit call.
- Ordinary words that are also skill names (`docs`, `pdf`, `docx`) are filtered
  as noise, so re-check those by hand.

## Fixing what it reports

1. Class A on a step that must run: rewrite to `Call the Skill tool with "x"`.
2. Class A in a cross-reference or index: leave it, it is documentation.
3. Class C: rephrase to tell the user, or remove the dependency.
4. Collision on one name across two dirs in the same root: one is unreachable.
   Delete, rename, or move the loser. Re-run until it clears.

## Pitfalls

- A name collision is invisible in the skill list, so it survives review. Grep
  for the directory, not the display name.
- A mirrored skill in a second tree is fine. The hazard is a second directory
  inside the *same* root, where the loader can only bind one.
- Do not convert prose cross-references wholesale. Most are an index, not a
  dependency, and rewriting them adds tokens without fixing a load.