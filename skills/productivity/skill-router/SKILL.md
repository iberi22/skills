---
name: skill-router
description: "Use when dispatching a subagent, choosing which skill to load, or deciding whether a task needs a skill at all. Maps task types to the exact skill name plus whether the model can auto-load it or the human must invoke it. Covers the 37 Matt Pocock skills and the SWAL orchestration set."
version: 1.0.0
license: MIT
---

# Skill Router — which skill, and who loads it

## The one rule that decides everything

A skill's frontmatter decides who may load it:

| Frontmatter | Who can load it |
|---|---|
| no `disable-model-invocation` | **model or human** — auto-loads when the description matches |
| `disable-model-invocation: true` | **human only** — no skill, and not the model, can ever load it |

To use a human-only skill, the human asks for it by name. Do not tell them a skill
"cannot" be used; tell them it needs their explicit request.

## Dispatch checklist

1. Does a skill cover this task? Match on the task type, not the vocabulary.
2. Check its invocation mode (table above).
3. Human-only → include `skill_view(name='<skill>')` in the subagent's `context` so the child loads it as its first action.
4. Model-loadable → say nothing; it fires on its own.
5. No skill covers it → do the work. Do not load a near-match.

## Orchestration and delegation

| Task | Skill | Mode |
|---|---|---|
| Spawn subagents, set concurrency | `subagent-launcher` | auto |
| Pick a model/provider | `llm-routing` | auto |
| Check host resources first | `llm-resource-monitor` | auto |
| Build Jules issues (canonical template) | `gitcore-jules-issues` | auto |
| Run a Jules wave (7 phases) | `jules-wave-orchestration` | auto |
| Jules two-pass CI protocol | `jules` | auto |
| Merge agent PRs in batches | `agent-pr-integration` | auto |
| Recover a failed Jules session | `jules-recovery-protocol` | auto |
| Watch async agents | `async-agent-monitoring` | auto |
| Several agents, one shot | `adhd` | auto |
| Subagents that must self-skill | this file + `context` field | — |

**Give the child the skill by name in `context`.** A subagent's system prompt is built
fresh from `goal` + `context` (`_build_child_system_prompt`); it does not inherit the
parent's skill catalog. Put `skill_view(name='X')` in `context` and the child loads it
as its first action.

## Engineering (Matt Pocock v1.3.1, 37 skills)

### Auto-loadable — safe to rely on

| Skill | Use for |
|---|---|
| `tdd` | red→green loop, test-first, vertical slices |
| `pr` | the **body** of a PR: visual summary, before/after evidence, merge-danger call |
| `code-review` | review with a hard gate; use after implementation |
| `diagnosing-bugs` | systematic root-cause search |
| `codebase-design` | module / interface / seam / depth vocabulary |
| `domain-modeling` | write `GLOSSARY.md` and ADRs |
| `research` | web research |
| `prototype` | throwaway prototype answering one question |
| `writing-for-agents` | how to write skills for agents |
| `wizard` | a procedure only a human can perform (clicks, approvals) |
| `setup-pre-commit` | add a pre-commit hook |
| `grilling` | decision interview (loads when `grill-me` runs) |
| `migrate-to-shoehorn`, `scaffold-exercises`, `git-guardrails-claude-code` | narrow helpers |

### Human-only — must be requested

| Skill | Use for |
|---|---|
| `to-spec` | conversation → spec, published to the tracker |
| `to-tickets` | spec → tickets |
| `issue-triage` | move issues through triage states (**not** bug diagnosis; that is `bug-triage`) |
| `implement` / `implement-spec` | implement a ticket / a whole spec |
| `wayfinder` | chart work too big for one session |
| `retro` | retrospective on a session's agent environment |
| `improve-codebase-architecture` | architecture pass |
| `grill-me` / `grill-with-docs` | start a grilling session |
| `handoff`, `claude-handoff`, `wait-what`, `teach`, `to-questionnaire` | session continuity and docs |
| `writing-beats`, `writing-fragments`, `writing-shape` | fiction workflow |
| `setup-matt-pocock-skills` | writes `docs/agents/`; assumes GitHub sub-issues — **rarely wanted here** |
| `setup-ts-deep-modules`, `loop-me` | narrow |

## Overlaps — pick one deliberately

| Two skills | Resolution |
|---|---|
| `mattpocock/tdd` vs `rust-development/tdd` | different names; both loadable. Pick by language. |
| `issue-triage` vs `bug-triage` | renamed from two skills both called `triage`: `issue-triage` moves issues through states; `bug-triage` diagnoses bugs. |
| `mattpocock/code-review` vs `github/github-code-review` | former is the review pass, latter is `gh` mechanics. Often both. |
| `mattpocock/prototype` vs `_archive/prototype` | archive is discoverable too; prefer the Matt one. |
| `mattpocock/diagnosing-bugs` vs `software-development/systematic-debugging` | near-identical intent. Either. |

## Do not

- Load a skill "to be safe". A near-match costs read tokens and adds nothing.
- Tell a human a human-only skill is unavailable — it needs their request, not permission.
- Assume a human-only skill can be reached by another skill. It cannot, ever.
- Put a whole SKILL.md body in `context`. Point at the name; the child loads it.