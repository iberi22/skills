---
name: agentic-e2e
description: "Agentic end-to-end testing with tester-army/e2e (npm `e2e`): natural-language agent steps with exact assertions, a replay cache that reruns verified steps without model calls, `e2e explore` and bug bashes that prove each finding with a failing repro test, and an MCP server to check locators against the live app. Use when planning exploratory QA before a demo or release, when deciding whether to add agentic tests next to a Playwright suite, or when a project already has e2e.config.ts."
---

# Agentic E2E (tester-army/e2e)

Evaluated 2026-10-02 against `github.com/tester-army/e2e` (v0.16.0, Apache-2.0, pre-1.0: APIs and config
still change between minor releases). **Not adopted in any SWAL repo yet.** This skill says where it fits next to
our Playwright suites and how to trial it safely. For the API itself, install it and read the upstream guide:
`npx e2e guide <topic>` (topics: setup, writing-tests, agent, running, explore, debugging, mcp, bug-bash);
the full docs ship in `node_modules/e2e/docs`.

## What it adds that Playwright does not

| Capability | Why it matters for us |
|---|---|
| `agent.act('goal')` + `agent.assert('...')` with `expect`/`screen` in the same test | Flows survive copy/layout changes (the GARA-G theme migration broke many text/role selectors at once). |
| Replay cache: a verified `agent.act` step reruns its recorded actions with **no model call**; if a control or end state no longer matches, the agent takes over from the current screen | Cost only on first run and after UI changes; `--no-cache` rules the cache out of a failure. Wrap timestamps/emails in `unique()` or every run misses. |
| `e2e explore '<goal>'` (8 steps / 10 min default budgets) → findings with expected vs observed, repro steps, screenshot, severity 1–5 | Finds the bugs no scripted spec was written for. |
| Bug bash: 5–10 one-sentence charters by persona run 4 at a time, each finding kept **only if a repro test fails with `ASSERTION_FAILED`** | Matches our "a cheap model's finding is a claim, not evidence" rule (llm-routing). |
| `e2e mcp`: a coding agent opens a session, `observe`/`locate` the live app before writing a locator | Kills the most common outdated-selector failures we see from subagent-written specs. |
| Machine-readable `.e2e/report.json`, stable error codes (`LOCATOR_AMBIGUOUS`, `ASSERTION_FAILED`, ...), `credentials`/`secrets` resolved by name | Subagents can triage without screenshots; secrets never enter test code or model context. |

## What it does not do yet (keep Playwright for these)

From its own Playwright migration table: no `colorScheme`, `locale`, `timezoneId`, `geolocation`, `permissions`;
no `devices[...]`, `isMobile`, `hasTouch`, `deviceScaleFactor` (viewport size only); no `globalSetup`, no HTML
reporter, no `fullyParallel`; `webServer` arrays don't start dependency processes. Our light/dark × desktop/touch
specs and visual sweeps therefore stay in Playwright.

Model: there is no default; agent steps need a model with tool calls **and** images. **Claude subscriptions are
not supported** (API key, GitHub Copilot, ChatGPT/SuperGrok sign-in, OpenRouter, Vercel AI Gateway, or a local
OpenAI-compatible endpoint). Pick it with `llm-routing`; the shared ChatGPT account is quota-protected, so
don't point a bug bash at it without asking. Tests with no agent steps need no model.

Telemetry is **on by default** (anonymous usage data): set `E2E_TELEMETRY_DISABLED=1` in the env/CI of any
private repo, or run `npx e2e telemetry disable`.

## How to trial it in a SWAL app (recommended order)

1. **Bug bash before a demo/release, no test files committed** — highest value, lowest commitment:
   start a production build/preview (not the dev server: a route compiling on first visit looks like a dead
   link to an explorer, and our Astro+workerd dev server also wipes in-memory data on reload), then one
   `npx e2e explore` per charter with its own `--output`. Personas = the real clients (e.g. GARA-G: trucking
   fleet manager, yellow-machinery owner tracking engine hours, a rider maintaining their own motorbike).
   Keep only findings whose repro test fails; reject the ones explained by seed data or the local environment.
2. **A few agentic smoke journeys** for the flows that must never break (login → dashboard, create vehicle,
   onboarding), in `tests/**/*.e2e.ts` beside the Playwright `*.spec.ts` (different globs, same project).
3. Only then consider migrating brittle Playwright specs one file at a time.

Prerequisites to check first: `@e2e-dev/web` needs Playwright `>=1.63.0 <2` (GARA-G had 1.62.1 on 2026-10-02 →
bump first); sign-in goes through `test.setup` + `{ session }` (no `storageState` file import), so write a setup
that signs in through the UI or sets the session the app expects.

## Rules (theirs and ours)

- One goal per `agent.act`, pinned right after by `expect` or `agent.assert`. Exact values (a password, a
  count, a specific string) go through `screen`, not the agent.
- Never add a sleep: actions wait for readiness and `expect` retries.
- Repro tests stay out of the merge-gating suite until the bug is fixed; then they become regression tests.
- Against a shared deployed site a bash is read-only: no sign-ups, submissions or injection-shaped URLs.

Related: `gentleman-playwright` (deterministic specs), `test-writer-fixer` (repairing specs),
`test-results-analyzer` (triage), `bateria-de-testing` (where this sits in a full pass), `browser-automation`
(building in-app browser agents, a different problem).
