---
name: bug-triage
slug: bug-triage
version: 1.0.0
description: Use when diagnosing a bug in code. Five steps: understand the symptom, form hypotheses, test each with the smallest experiment, isolate the root cause, then fix with a regression test. For issue-tracker states and roles, use issue-triage.
license: MIT
original_source: https://github.com/mattpocock/skills
category: debugging
tags: [triage, debugging, bug, diagnosis, root-cause, workflow]
goals:
  - Diagnose bugs systematically, not at random
  - Shorten the time from symptom to root cause
  - Test hypotheses with the smallest possible experiment
  - Document findings to avoid similar bugs
context:
  when: A bug, error, or unexpected behavior is reported
  who: Any coding agent
  prerequisites: Access to the code and system logs
authors:
  - mattpocock (original repo)
  - Brahyan Belalcazar (structured version)
---

# Bug triage — bug diagnosis workflow

This skill sets a systematic 5-step process for diagnosing bugs without changing code at random. Each step produces information that feeds the next.

## Principles

1. **Do not touch code without a hypothesis.** If you do not know what you are testing, you are guessing.
2. **The smallest experiment wins.** Narrow the scope until the answer is yes or no.
3. **Reproduce before diagnosing.** If you cannot reproduce it, you cannot confirm the fix.
4. **Document at each step.** A bug unresolved today is useful information tomorrow.

---

## Step 1: Understand the symptom

Before touching code, characterize the problem:

- What is expected vs. what happens?
- Is it consistent or intermittent?
- Which environment? (local, staging, production)
- When did it start? What changed just before?
- Are there stack traces, logs, or error messages?

**Deliverable:** A 2–3 line paragraph describing the symptom without naming causes.

---

## Step 2: Form hypotheses

Generate 2–4 plausible explanations, ordered by likelihood. Use your knowledge of the system, not vague intuitions.

Format of each hypothesis:

```
H1: <what is failing> → <why you think so> → <which experiment confirms or rejects it>
```

Example:

```
H1: The auth service returns 401 because the token expires earlier than expected.
    → The bug occurs only after 15 min of inactivity.
    → Experiment: log the token TTL at the moment of the 401.
```

---

## Step 3: Test with the smallest possible experiment

For each hypothesis, design an experiment that is:

- **Fast:** under 10 minutes of setup.
- **Isolated:** does not depend on other systems where possible.
- **Binary:** produces a result that confirms or rejects the hypothesis.

Useful techniques:

| Technique | When to use it |
|---|---|
| **Log points** | You need variable values at runtime without stopping the flow. |
| **Binary search in git** | The bug appeared in some recent commit. Use `git bisect`. |
| **Minimal reproduction** | Remove dependencies, code, and data until the bug still occurs in the smallest possible setup. |
| **Temporary monkey-patch** | Force a value or bypass to confirm whether a dependency is the culprit. |
| **State diff** | Compare system state (DB, cache, config) between a working and a failing environment. |

**Rule:** If an experiment does not halve the search space, it is too big.

---

## Step 4: Isolate the root cause

When a hypothesis is confirmed, keep digging until you find the root cause, not just the symptom.

Guiding questions:

- Is it a bug in my code or in a dependency?
- Is it a logic, configuration, or data error?
- Why does this input produce this output? Follow the data flow.
- Is an invariant being broken? Where should it have been validated?

**Deliverable:** One sentence explaining the root cause, linking the defect to the observable effect.

---

## Step 5: Fix + regression test

1. **Fix the minimum necessary.** A large fix is suspicious.
2. **Verify the fix works.** Reproduce the bug with the Step 1 steps; it must disappear.
3. **Add a regression test.** If possible, write a test that fails before the fix and passes after.
4. **Document briefly.** Note in the commit or a doc why it happened and how to avoid it.

---

## Anti-patterns to avoid

- **Changing code and seeing what happens.** This destroys information.
- **Debugging without reproducing first.** You lose confirmation of success.
- **Assuming the bug is "obvious".** The root cause is usually 2–3 levels below the symptom.
- **Jumping to a fix without a confirmed hypothesis.** You fix the symptom, not the bug.

---

## Quick checklist

- [ ] Symptom clearly described
- [ ] Hypotheses written and ordered
- [ ] Minimal experiment run
- [ ] Root cause identified
- [ ] Fix applied and verified
- [ ] Regression test added
- [ ] Findings documented
