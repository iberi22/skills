---
name: prototype
slug: prototype
version: 1.0.0
description: Workflow for rapid feature prototyping. Prioritizes speed over quality, disposable code over maintainable code, and hypothesis validation over robustness. Shifts the mindset from "production" to "experiment".
license: MIT
original_source: https://github.com/mattpocock/skills
category: engineering-workflow
tags: [prototype, rapid, mvp, experiment, proof-of-concept, workflow]
goals:
  - Validate technical hypotheses in the least possible time
  - Shift the mindset from production to experiment
  - Reduce the cost of exploring solutions
  - Decide quickly whether to continue or pivot
context:
  when: You need to validate an idea, test an approach, or build a POC
  who: Any coding agent
  prerequisites: Basic knowledge of the problem domain
  avoid_when: The code goes straight to production without refactoring
---

# Prototype

> Adapted from mattpocock/skills `prototype` (MIT): https://github.com/mattpocock/skills

A prototype is **disposable code that answers one question**. The question defines the shape.

It does not matter whether the question is about business logic, a state machine, an API, or a user interface. A prototype exists only to validate one concrete hypothesis in the least possible time. If there is no clear question, there is no prototype.

## Pick a branch

Identify which question you are answering, from the user's prompt, the surrounding code, or by asking directly:

- **"Does this logic / state model feel right?"** → Build a small interactive terminal app that exercises the state machine on cases that are hard to reason about on paper.
- **"What should this look like?"** → Generate several visually distinct UI versions on a single route, switchable via a query param and a floating selection bar.

The two branches produce very different artifacts. Choosing the wrong one wastes the prototype's effort. If the question is genuinely ambiguous and the user is unavailable, pick the branch that best matches the surrounding code (backend module → logic; page or component → UI) and state the assumption at the top of the prototype.

## Prototype mindset

Hold these principles throughout the prototyping cycle:

1. **Speed > quality.** The goal is to learn, not to ship polished code. Every minute counts.
2. **Disposable > maintainable.** Do not invest in abstractions, tests, extensive documentation or architectural patterns. This will be thrown away.
3. **Validation > robustness.** If it fails on a non-critical edge case or does not handle network errors, that does not matter. The goal is to confirm or refute the core hypothesis.
4. **One command to run.** Use the project's runner (`pnpm dev`, `python script.py`, `bun run`, etc.). The user must be able to start it without reading instructions.
5. **No persistence by default.** State lives in memory. If the question involves a database, use a scratch DB or a local file with an unambiguous name such as `PROTOTYPE_data.json` or `scratch.sqlite`.
6. **Expose the state.** After every action, print or render the full relevant state so it is visible what changed and why.
7. **Assume it will fail.** Most prototypes confirm that an idea does not work. That is also a success: you avoided weeks of investment in an invalid solution.

## Rapid prototyping techniques

Apply these tactics to maximize speed and minimize friction:

- **Deliberate copy-paste:** Copy code from official docs, StackOverflow, GitHub examples or earlier projects without guilt. Do not refactor; paste and adjust the minimum needed to make it work.
- **Mock before real:** Use fake data, stubs and mocks. Do not connect to real APIs, external services or production queues if static JSON or a synchronous function answers the question.
- **Hardcode before configurable:** If a value rarely changes in the experiment's context, write it directly in the code. Do not add `config.ts`, environment variables, `.env` files or CLI flags.
- **Ignore types and lint if they slow you down.** If the project uses TypeScript or a strict linter, use `any`, `@ts-ignore`, or disable rules locally if that lets you move faster. Do not redefine full interfaces for a prototype.
- **UI: multiple radical variations.** If the question is "what should this look like?", generate several visually distinct versions on one route or page. Switch between them with a query param (e.g. `?variant=A`) and a floating selection bar. Do not build real navigation.
- **Logic: interactive terminal.** If the question is "does the state model or business logic make sense?", build a small terminal app that exercises the state machine on cases that are hard to reason about on paper. Let the user interact with simple commands.
- **No versions, no intermediate commits.** Work in a single file or on the branch closest to the goal. Do not spend time on a clean git history for code that will be deleted.

## Boundary conditions: when to stop

Recognizing when to stop is crucial. A prototype that keeps growing stops being an experiment and becomes disguised technical debt:

- **The question was answered.** You have enough information to decide whether the idea is viable or whether to pivot.
- **The cost of continuing exceeds the expected benefit.** If fixing the prototype for an edge case takes longer than rebuilding it cleanly from scratch, stop immediately.
- **An unknown blocker was found.** The prototype did its job by revealing a risk, technical limitation or blocking dependency that invalidates the approach.
- **More than 2-4 hours of net work have passed.** An effective prototype should answer its question in a few hours. If it runs longer, you are probably building something bigger than needed.
- **You start adding unit tests, exhaustive error handling or structured logging.** That is a clear signal: you are no longer in experiment mode; you are writing production code without noticing.
- **Someone says "this is almost ready to deploy".** That phrase is a trap. Stop, validate the hypothesis, then re-plan.

## Moving to production

Never promote a prototype directly to production. Disposable code is designed to be deleted, not to evolve:

1. **Do not turn the prototype into production directly.** Even if it "works", it is full of shortcuts, intentional debt and unvalidated assumptions.
2. **Extract the validated decision.** Capture the answer in an ADR, a descriptive commit message, a follow-up issue, or a `NOTES.md` next to the original question.
3. **Document the findings.** Note what worked, what did not, which edge cases were ignored, and which architectural decisions came out of the experiment.
4. **Rewrite from scratch with production mindset.** Now that you know the approach is viable, design the robust, testable, maintainable and secure solution.
5. **Delete the prototype.** Do not leave dead code in the repository. Either absorb it explicitly into the new implementation or remove it entirely. Do not comment it out or move it to an `_old` folder.

## Shared rules across branches (Logic / UI)

Whether the prototype is logic or interface, these rules always apply:

1. **Disposable from day one, clearly marked.** Place the code near where it will eventually live (same module, same page, same folder) but with an obvious prototype name (e.g. `prototype-cart.ts`, `PlaygroundVariants.tsx`, `/prototype/page.tsx`). Do not invent a new route structure or a root-level `experiments/` directory.
2. **No polish.** No tests, no error handling beyond the minimum needed to run, no generic abstractions, no i18n, no analytics. The point is to learn fast, then delete.
3. **Delete or absorb when done.** Once the prototype has answered its question, delete it or integrate the validated decision into the real code. Do not let it rot in the repository for weeks.

## Wrap-up

The **answer** is the only thing worth keeping from a prototype. The code itself is irrelevant once its purpose is served.

If the user is available at the end, capture the answer in a quick conversation and decide together whether to absorb, rewrite or discard. If the user is not available, leave a clear placeholder (a `TODO` or a `NOTES.md`) so it can be completed before the prototype is deleted for good.

Remember: a good prototype is one that lets you decide quickly. Sometimes the best decision is "it does not work, let's drop this idea". That saves weeks of work.
