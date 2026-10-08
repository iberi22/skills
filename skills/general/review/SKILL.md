---
name: review
description: Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes — Standards (does the code follow this repo's documented coding standards?) and Spec (does the code match what the originating issue/PRD asked for?). Runs both reviews in parallel sub-agents and reports them side by side. Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to "review since X".
metadata:
  author: swal
  version: "2.1.0"
  openclaw:
    autoLoad: false
    forSubagents: true
    lightContext: true
---

# Review Skill v2 — Two-Axis Code Review

> 🔍 Parallel review of a diff along Standards + Spec axes using sub-agents.

Two-axis review of the diff between `HEAD` and a fixed point the user supplies:

- **Standards** — does the code conform to this repo's documented coding standards?
- **Spec** — does the code faithfully implement the originating issue / PRD / spec?

Both axes run as **parallel sub-agents** so they don't pollute each other's context, then this skill aggregates their findings.

Fetch issues with `gh issue view` (or the tracker the repo documents).

## Process

### 1. Pin the fixed point

Whatever the user said is the fixed point — a commit SHA, branch name, tag, `main`, `HEAD~5`, etc. If they didn't specify one, ask for it.

Capture the diff command once: `git diff <fixed-point>...HEAD` (three-dot, so the comparison is against the merge-base). Also note the list of commits via `git log <fixed-point>..HEAD --oneline`.

Before going further, confirm the fixed point resolves (`git rev-parse <fixed-point>`) and the diff is non-empty. A bad ref or empty diff should fail here — not inside two parallel sub-agents.

### 2. Identify the spec source

Look for the originating spec, in this order:

1. Issue references in the commit messages (`#123`, `Closes #45`, GitLab `!67`, etc.) — fetch via `gh issue view`.
2. A path the user passed as an argument.
3. A PRD/spec file under `docs/`, `specs/`, or `.scratch/` matching the branch name or feature.
4. If nothing is found, use the **PR description** and linked **issue body** as the spec. If neither exists, ask the user. If they say there isn't one, the **Spec** sub-agent will skip and report "no spec available".

### 3. Identify the standards sources

Anything in the repo that documents how code should be written, such as `CODING_STANDARDS.md` or `CONTRIBUTING.md`.

On top of whatever the repo documents, the Standards axis always carries the **smell baseline** below — a fixed set of Fowler code smells (_Refactoring_, ch.3) that applies even when a repo documents nothing. Two rules bind it:

- **The repo overrides.** A documented repo standard always wins; where it endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic, never a hard violation — and, like any standard here, skip anything tooling already enforces.

## Smell Baseline (Fowler)

Each smell reads **what it is → how to fix it**. Match each against the diff and report any hit.

| # | Smell | What It Is | How To Fix It |
|---|-------|-----------|---------------|
| 1 | **Mysterious Name** | A function, variable, or type whose name doesn't reveal what it does or holds. | Rename it; if no honest name comes, the design's murky. |
| 2 | **Duplicated Code** | The same logic shape appears in more than one hunk or file in the change. | Extract the shared shape, call it from both. |
| 3 | **Long Function** | A function doing too much in one go — more than ~20 lines or 3 levels of nesting. | Extract method/function for each distinct concern. |
| 4 | **Long Parameter List** | 3+ parameters that travel together or could be grouped. | Bundle related params into one type, pass that. |
| 5 | **Global Data** | Mutable global/shared state that any part of the code can touch. | Wrap behind an interface; scope to the smallest possible boundary. |
| 6 | **Mutable Data** | Data that could be immutable but isn't — fields mutated after construction, let mut that could be let. | Prefer immutable by default; use interior mutability patterns only when required. |
| 7 | **Divergent Change** | One file or module is edited for several unrelated reasons in the diff. | Split so each module changes for one reason. |
| 8 | **Shotgun Surgery** | One logical change forces scattered edits across many files in the diff. | Gather what changes together into one module. |
| 9 | **Feature Envy** | A method that reaches into another object's data more than its own. | Move the method onto the data it envies. |
| 10 | **Data Clumps** | The same 3+ fields or params keep travelling together — a type wanting to be born. | Bundle them into one type, pass that. |
| 11 | **Primitive Obsession** | A primitive `String`, `i32`, `u64`, `bool` standing in for a domain concept that deserves its own type. | Give the concept its own small newtype. |
| 12 | **Repeated Switches** | The same `match`/`if`-cascade on the same type recurs across the change. | Replace with polymorphism/trait dispatch, or one map both sites share. |
| 13 | **Speculative Generality** | Abstraction, parameters, or hooks added for needs the spec doesn't have. | Delete it; inline back until a real need shows. |
| 14 | **Temporary Field** | A field only set in some code paths, left unused in others. | Extract into a separate struct returned by the path that uses it. |
| 15 | **Message Chains** | Long `a.b().c().d()` navigation the caller shouldn't depend on. | Hide the walk behind one method on the first object. |
| 16 | **Middle Man** | A class or function that mostly just delegates onward, adding no value. | Cut it, call the real target direct. |
| 17 | **Insider Trading** | Modules that exchange too much private data across boundaries. | Reduce the surface area; pull the interaction into a shared module. |
| 18 | **Large Class** | A struct with too many fields or too many impl blocks for unrelated concerns. | Split into smaller structs, each with one responsibility. |
| 19 | **Alternative Classes with Different Interfaces** | Similar domain concepts handled by structurally different APIs. | Unify behind a trait or enum interface. |
| 20 | **Data Class** | A struct with only public fields and trivial getters — no behaviour. | Move behaviour in; protect fields behind methods when invariants exist. |
| 21 | **Refused Bequest** | A type that implements or inherits a trait/interface but ignores most of its contract. | Swap inheritance for composition; break the trait into smaller ones. |
| 22 | **Lazy Element** | A struct, enum variant, or module that doesn't earn its keep — just one field or one trivial function. | Inline it; delete the wrapper. |
| 23 | **Loops** | A `for`/`while` that could be a pipeline (map/filter/reduce/fold). | Replace with iterator combinators. |
| 24 | **Comments** | A comment explaining *what* the code does, when a better name or clearer expression would make it obvious. | Remove the comment; rename or restructure until the code speaks for itself. |

### Baseline rules

- **The repo overrides.** A documented repo standard always wins; where it endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic, never a hard violation. Skip anything tooling (clippy, rustfmt, cargo deny) already enforces.

## 4. Launch parallel sub-agents

Launch **both sub-agents in a single message** with the Agent tool so they run in parallel; each returns its report as its final message.

### Standards sub-agent prompt

Include:

- The full diff command and commit list.
- The list of standards-source files you found in step 3, **plus the smell baseline from step 3** pasted in full — the sub-agent has no other access to it.
- **Brief:** "Report — per file/hunk where relevant — (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) any baseline smell you spot: name it and quote the hunk. Distinguish hard violations from judgement calls — documented-standard breaches can be hard, but baseline smells are always judgement calls, and a documented repo standard overrides the baseline. Skip anything tooling enforces. Keep it scannable: one line per finding with the quoted hunk; no preamble."

### Spec sub-agent prompt

Include:

- The diff command and commit list.
- The path or fetched contents of the spec (PR description + linked issue body).
- **Brief:** "Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong. Quote the spec line for each finding. Keep it scannable: one line per finding; no preamble."

If the spec is missing, skip the Spec sub-agent and note this in the final report.

## 5. Aggregate

Present the two reports under `## Standards` and `## Spec` headings, verbatim or lightly cleaned. Do **not** merge or rerank findings — the two axes are deliberately separate (see *Why two axes*).

End with a **verdict row** per PR:

| Axis | Finding Count | Worst Issue |
|------|--------------|-------------|
| Standards | N findings | ... |
| Spec | N findings | ... |

Don't pick a single winner across axes — that's the reranking the separation exists to prevent.

### Verdict helpers

| Pattern | Verdict |
|---------|---------|
| 0 smells + spec ✅ | **Clean.** Ship it. |
| 🟡 smells only + spec ✅ | **Needs polish** — address smells before merge. |
| 🔴 smells + spec ✅ | **Fix smells first** — high-severity issues block. |
| spec ⚠️/❌ (any smells) | **Fix spec gaps first** — correctness over style. |
| spec ❓ | **Needs discussion** — unclear requirements. |

## Why two axes

A change can pass one axis and fail the other:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the issue asked but breaks the project's conventions → **Spec pass, Standards fail.**

Reporting them separately stops one axis from masking the other.

## Execution

Run the steps in order:

1. Resolve the fixed point
2. Collect diff + commits
3. Find spec + standards sources
4. **Launch both sub-agents** (parallel)
5. **Wait for both** reports
6. **Aggregate** into the combined report
7. **Present** the final output
