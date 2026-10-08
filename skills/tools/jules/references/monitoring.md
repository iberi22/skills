# Monitoring: sessions, PRs, outcomes

## Map a session to its PR

Jules branches start with `jules-`. A session ID may appear in the branch name.

```bash
# By session ID
git ls-remote --heads origin | grep "<session-id>"
gh pr list --state all --head "<branch-name>" --json number,state --jq '.[0].number'

# All Jules PRs (prefix match, not author match)
gh pr list --state all -L 30 --json number,title,state,headRefName,createdAt --search "head:jules-"

# PRs by author (includes other automation under the same account)
gh pr list --author <github-user> --state all -L 20 --json number,title,state,headRefName
```

Session ID and PR must be cross-checked: the branch name is the link, not the title.

## PR outcome

| PR state | Meaning | Action |
|---|---|---|
| OPEN | Pending review | Gate and merge (`SKILL.md` §7) |
| MERGED | Success | Done |
| CLOSED, not merged | A person rejected it | Find out who and why before reopening or discarding |
| No PR; session COMPLETED | False positive or code without PR | `patch` the session; if no code, record as no output |

Who closed a PR:

```bash
gh api repos/<owner>/<repo>/issues/<pr-number>/events \
  | python3 -c "import sys,json; [print(f'{e[\"event\"]} by {e[\"actor\"][\"login\"]} at {e[\"created_at\"]}') for e in json.load(sys.stdin) if e.get('event') in ('closed','merged')]"
```

Session ID and branch name: the link is the PR's `headRefName`, not the title. Branch names can be descriptive and carry the session ID as a suffix, or not carry it at all. Check with `gh pr view <num> --json headRefName` instead of guessing.

## Classify a stuck session

Use only after the session has been in AWAITING_USER_FEEDBACK (or PLANNING) for over an hour with no PR or branch.

| Classification | Pattern | Response |
|---|---|---|
| True stuck | Isolated; pull gives no output; no PR or branch | Answer once (§6.1 of `SKILL.md`); if still nothing, archive, rewrite the brief with more context, relaunch under a new title |
| Systemic block | Two or more agents stuck at once, no PRs, similar ages, and another session of the same type completed | Escalate one batch to a person. Likely a shared approval gate. Do not re-trigger each one |
| Already obsolete | A PR for the same work exists under another session | Archive the stuck session; close its issue if one exists |
| Transient | Resolved by itself within the window | No action; widen the threshold |

Escalate to a person immediately if:
- a systemic block is detected;
- a session has been AWAITING with no PR for more than 6 h;
- a session is AWAITING and its source issue no longer has the trigger label;
- the same session reappears as stuck after a re-trigger.

## Session state vs. outcome

- COMPLETED with no PR: check the last patch and the branch list. Code may exist without a PR (the session was created without `AUTO_CREATE_PR`).
- A missing session in the CLI list does not mean no work happened. Paginate the API for full history, then triangulate.
- A PR with a small line count against a large brief: check the parts gate (`SKILL.md` §7).

## Triangulate when the CLI or API is unavailable

Use at least three independent sources:

```bash
gh issue list --label <label> --state all --json number,title,state,updatedAt --limit 20   # label path only
gh pr list --author <github-user> --state all -L 20 --json number,title,state,headRefName,createdAt
git fetch origin --quiet
git for-each-ref --sort=-committerdate refs/remotes/origin \
  --format='%(committerdate:relative)|%(refname:short)' | grep -v "main\|HEAD" | head -10
```

Reading the result:
- Sessions empty, issues or PRs still pending: execution is done. Move to review and merge.
- Sessions active, no PR after a long time: check the session state before concluding anything.
- Do not treat `gh api repos/<owner>/<repo>/activity` as reliable. It returned empty data for some repos without errors.

## Recurring reports

- Report "no change" for items whose state did not change since the last report. Persist the last known state (a file or memory) to detect real changes.
- Use the same source set every time, and say which sources were unavailable.
