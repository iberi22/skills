---
name: playwright
description: >
  Playwright E2E testing patterns.
  Trigger: When writing E2E tests - Page Objects, selectors, MCP workflow.
license: Apache-2.0
updated: "2026-10-02"
metadata:
  author: gentleman-programming
  version: "1.2"
---

## MCP Workflow

If Playwright MCP tools are available, explore the target flow first (snapshot, interact, note real roles and labels) so selectors come from the live DOM, not guesses.

**If MCP NOT available:** Proceed with test creation based on docs and code analysis.

**Why This Matters:**
- ✅ Precise tests - exact steps needed, no assumptions
- ✅ Accurate selectors - real DOM structure, not imagined
- ✅ Real flow validation - verify journey actually works
- ✅ Avoid over-engineering - minimal tests for what exists
- ✅ Prevent flaky tests - real exploration = stable tests
- ❌ Never assume how UI "should" work

## File Structure

```
tests/
├── base-page.ts              # Parent class for ALL pages
├── helpers.ts                # Shared utilities
└── {page-name}/
    ├── {page-name}-page.ts   # Page Object Model
    ├── {page-name}.spec.ts   # ALL tests here (NO separate files!)
    └── {page-name}.md        # Test documentation
```

**File Naming:**
- ✅ `sign-up.spec.ts` (all sign-up tests)
- ✅ `sign-up-page.ts` (page object)
- ✅ `sign-up.md` (documentation)
- ❌ `sign-up-critical-path.spec.ts` (WRONG - no separate files)
- ❌ `sign-up-validation.spec.ts` (WRONG)

## Selector Priority (REQUIRED)

```typescript
// 1. BEST - getByRole for interactive elements
this.submitButton = page.getByRole("button", { name: "Submit" });
this.navLink = page.getByRole("link", { name: "Dashboard" });

// 2. BEST - getByLabel for form controls
this.emailInput = page.getByLabel("Email");
this.passwordInput = page.getByLabel("Password");

// 3. SPARINGLY - getByText for static content only
this.errorMessage = page.getByText("Invalid credentials");
this.pageTitle = page.getByText("Welcome");

// 4. LAST RESORT - getByTestId when above fail
this.customWidget = page.getByTestId("date-picker");

// ❌ AVOID fragile selectors
this.button = page.locator(".btn-primary");  // NO
this.input = page.locator("#email");         // NO
```

## Scope Detection (ASK IF AMBIGUOUS)

| User Says | Action |
|-----------|--------|
| "a test", "one test", "new test", "add test" | Create ONE test() in existing spec |
| "comprehensive tests", "all tests", "test suite", "generate tests" | Create full suite |

**Examples:**
- "Create a test for user sign-up" → ONE test only
- "Generate E2E tests for login page" → Full suite
- "Add a test to verify form validation" → ONE test to existing spec

## Page Object Pattern

```typescript
import { Page, Locator, expect } from "@playwright/test";

// BasePage - ALL pages extend this
export class BasePage {
  constructor(protected page: Page) {}

  async goto(path: string): Promise<void> {
    await this.page.goto(path);
    await this.page.waitForLoadState("networkidle");
  }

  // Common methods go here (see Refactoring Guidelines)
  async waitForNotification(): Promise<void> {
    await this.page.waitForSelector('[role="status"]');
  }

  async verifyNotificationMessage(message: string): Promise<void> {
    const notification = this.page.locator('[role="status"]');
    await expect(notification).toContainText(message);
  }
}

// Page-specific implementation
export interface LoginData {
  email: string;
  password: string;
}

export class LoginPage extends BasePage {
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;

  constructor(page: Page) {
    super(page);
    this.emailInput = page.getByLabel("Email");
    this.passwordInput = page.getByLabel("Password");
    this.submitButton = page.getByRole("button", { name: "Sign in" });
  }

  async goto(): Promise<void> {
    await super.goto("/login");
  }

  async login(data: LoginData): Promise<void> {
    await this.emailInput.fill(data.email);
    await this.passwordInput.fill(data.password);
    await this.submitButton.click();
  }

  async verifyCriticalOutcome(): Promise<void> {
    await expect(this.page).toHaveURL("/dashboard");
  }
}
```

## Page Object Reuse

Reuse existing page objects in `tests/` before creating new ones.

```typescript
// ✅ GOOD: Reuse existing page objects
import { SignInPage } from "../sign-in/sign-in-page";
import { HomePage } from "../landing/home-page";

test("User can sign up and login", async ({ page }) => {
  const signUpPage = new SignUpPage(page);
  const signInPage = new SignInPage(page);  // REUSE
  const homePage = new HomePage(page);      // REUSE

  await signUpPage.signUp(userData);
  await homePage.verifyPageLoaded();  // REUSE method
  await homePage.signOut();           // REUSE method
  await signInPage.login(credentials); // REUSE method
});

// ❌ BAD: Recreating existing functionality
export class SignUpPage extends BasePage {
  async logout() { /* ... */ }  // ❌ HomePage already has this
  async login() { /* ... */ }   // ❌ SignInPage already has this
}
```

**Guidelines:**
- Check `tests/` for existing page objects first
- Import and reuse existing pages
- Create page objects only when page doesn't exist
- If test requires multiple pages, ensure all page objects exist (create if needed)

## Refactoring Guidelines

### Move to `BasePage` when:
- ✅ Navigation helpers used by multiple pages (`waitForPageLoad()`, `getCurrentUrl()`)
- ✅ Common UI interactions (notifications, modals, theme toggles)
- ✅ Verification patterns repeated across pages (`isVisible()`, `waitForVisible()`)
- ✅ Error handling that applies to all pages
- ✅ Screenshot utilities for debugging

### Move to `helpers.ts` when:
- ✅ Test data generation (`generateUniqueEmail()`, `generateTestUser()`)
- ✅ Setup/teardown utilities (`createTestUser()`, `cleanupTestData()`)
- ✅ Custom assertions (`expectNotificationToContain()`)
- ✅ API helpers for test setup (`seedDatabase()`, `resetState()`)
- ✅ Time utilities (`waitForCondition()`, `retryAction()`)

**Before (BAD):**
```typescript
// Repeated in multiple page objects
export class SignUpPage extends BasePage {
  async waitForNotification(): Promise<void> {
    await this.page.waitForSelector('[role="status"]');
  }
}
export class SignInPage extends BasePage {
  async waitForNotification(): Promise<void> {
    await this.page.waitForSelector('[role="status"]');  // DUPLICATED!
  }
}
```

**After (GOOD):**
```typescript
// BasePage - shared across all pages
export class BasePage {
  async waitForNotification(): Promise<void> {
    await this.page.waitForSelector('[role="status"]');
  }
}

// helpers.ts - data generation
export function generateUniqueEmail(): string {
  return `test.${Date.now()}@example.com`;
}

export function generateTestUser() {
  return {
    name: "Test User",
    email: generateUniqueEmail(),
    password: "TestPassword123!",
  };
}
```

## Test Pattern with Tags

```typescript
import { test, expect } from "@playwright/test";
import { LoginPage } from "./login-page";

test.describe("Login", () => {
  test("User can login successfully",
    { tag: ["@critical", "@e2e", "@login", "@LOGIN-E2E-001"] },
    async ({ page }) => {
      const loginPage = new LoginPage(page);

      await loginPage.goto();
      await loginPage.login({ email: "user@test.com", password: "pass123" });

      await expect(page).toHaveURL("/dashboard");
    }
  );
});
```

**Tag Categories:**
- Priority: `@critical`, `@high`, `@medium`, `@low`
- Type: `@e2e`
- Feature: `@signup`, `@signin`, `@dashboard`
- Test ID: `@SIGNUP-E2E-001`, `@LOGIN-E2E-002`

## Test Documentation Format ({page-name}.md)

```markdown
### E2E Tests: {Feature Name}

**Suite ID:** `{SUITE-ID}`
**Feature:** {Feature description}

---

## Test Case: `{TEST-ID}` - {Test case title}

**Priority:** `{critical|high|medium|low}`

**Tags:**
- type → @e2e
- feature → @{feature-name}

**Description/Objective:** {Brief description}

**Preconditions:**
- {Prerequisites for test to run}
- {Required data or state}

### Flow Steps:
1. {Step 1}
2. {Step 2}
3. {Step 3}

### Expected Result:
- {Expected outcome 1}
- {Expected outcome 2}

### Key verification points:
- {Assertion 1}
- {Assertion 2}

### Notes:
- {Additional considerations}
```

**Documentation Rules:**
- ❌ NO general test running instructions
- ❌ NO file structure explanations
- ❌ NO code examples or tutorials
- ❌ NO troubleshooting sections
- ✅ Focus ONLY on specific test case
- ✅ Keep under 60 lines when possible

## Hardening rules

Each one cost a red suite or a false green in practice.

- **Scope cookies with `url`, never `domain: 'localhost'`.** The suite runs against `BASE_URL`
  (a loopback IP such as 127.0.0.1 plus a port, in CI and worktrees); a `localhost` cookie never travels there, so every authenticated spec
  bounced to `/login`. Put session setup in ONE helper (`helpers/auth.ts: useAdminSession(context)`) built from
  `new URL(process.env.BASE_URL)`; inline `addCookies` copies drift.
- **The helper must carry every cookie the middleware gates on**, not just the session (an onboarding gate may also need
  a cookie such as `onboarding=<userId>`, or the protected route redirects to onboarding). When the app adds a gate, update the helper, not 30 specs.
- **Hit the real verb.** A logout spec did `page.goto('/api/auth/logout')` (GET) on a POST-only endpoint: 404,
  and it passed without logging out. Use `request.post` and assert the `Set-Cookie` that ends the session.
- **No sleeps.** Wait on a locator, a URL (`waitForURL`), or a response; `expect` already retries.
- **Selectors from the live app**, never from memory: Playwright MCP / `codegen`, or `e2e mcp` (see
  tester-army/e2e). Prefer role + accessible name and `data-testid`; text selectors break on copy/theme changes.
- **Test the commit you claim.** Pin the worktree to the exact SHA and say it in the report. Two QA runs on
  re-reported bugs already fixed 10 commits later.
- **Classify every failure with evidence** — outdated test / real app bug / environment — and never weaken an
  assertion to get green. `test.skip` only for hardware/network the runner lacks, with why.
- **Prefer a production build/preview for long or parallel runs.** Astro+workerd dev servers recompile on first
  visit, can answer 500 "unable to find a component instance" for prerendered pages after a reload, and lose
  in-memory seed data when Vite reoptimizes: re-warm and re-seed before blaming the app.
- **Theme and device matrix**: set the theme before first paint with `context.addInitScript(() =>
  localStorage.setItem('<theme-key>', 'dark'))` (setting it after `goto` screenshots the default theme); mobile
  = `{ viewport: {width: 390, height: 844}, isMobile: true, hasTouch: true }`.
- **Headless screenshots can come out one flat color** (dark mode, `fullPage`, WebGL). Launch Chromium with
  `--use-angle=swiftshader`, detect single-color PNGs and retry with a viewport as tall as `scrollHeight`
  (a visual-sweep script can do both); WebGPU pages need a WebGL fallback flag (`?gl=1`).
- **Compile every template in unit tests**: a stray parenthesis in one
  shared `.astro` component took down seven pages and no spec caught it before a full e2e run.

For exploratory QA and bug bashes before a demo, layer tester-army/e2e on top; keep this
Playwright suite as the deterministic gate.

## Commands

```bash
npx playwright test                    # Run all
npx playwright test --grep "login"     # Filter by name
npx playwright test --ui               # Interactive UI
npx playwright test --debug            # Debug mode
npx playwright test tests/login/       # Run specific folder
```

## Keywords
playwright, e2e, testing, page object model, selectors, end-to-end, mcp
