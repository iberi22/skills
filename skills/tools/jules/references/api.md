# Jules REST API (v1alpha)

Base URL: `https://jules.googleapis.com/v1alpha`. Auth header: `x-goog-api-key: <key>`. Read the key from an environment variable at runtime. Never print it, never paste it into a brief.

Key check (401 = invalid or expired key; rotate it or use another account):

```bash
curl -s -o /dev/null -w "%{http_code}\n" -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sources?pageSize=1"
```

## Endpoints

| Call | Use |
|---|---|
| `POST /sessions` | Create. Body: `prompt`, `title`, `sourceContext: {source: "sources/github/<owner>/<repo>", githubRepoContext: {startingBranch: "<branch>"}}`, `automationMode: "AUTO_CREATE_PR"`, `requirePlanApproval` (bool). |
| `GET /sessions?pageSize=100&pageToken=…` | List, paginated. Full history, not only recent sessions. |
| `GET /sessions/{id}` | One session. |
| `GET /sessions/{id}/activities?pageSize=50&pageToken=…` | Activities, oldest-first. Follow `nextPageToken` to the end. |
| `GET /sources` | Repos connected to the account. |
| `POST /sessions/{id}:sendMessage` | Reply. Body exactly `{"prompt": "<text>"}`. Response `{}`. |
| `POST /sessions/{id}:approvePlan` | Approve a plan in `AWAITING_PLAN_APPROVAL`. |
| `POST /sessions/{id}:archive` | Archive. Not in the public docs; treat as undocumented. |

## States

- Non-terminal (hold a concurrency slot): `QUEUED`, `PLANNING`, `AWAITING_PLAN_APPROVAL`, `AWAITING_USER_FEEDBACK`, `IN_PROGRESS`, `PAUSED`.
- Terminal: `COMPLETED`, `FAILED`.

## Where the output is

- PR URL: `outputs[].pullRequest.url`.
- Code: `activities[].artifacts[].changeSet.gitPatch.unidiffPatch`. Each patch is cumulative.

## Activity fields

Fields are nested by type. A parser that reads `message` or `text` returns empty strings silently.

| Activity type | Field |
|---|---|
| Agent question | `agentMessaged.agentMessage` |
| User message | `userMessaged.userMessage` |
| Plan | `planGenerated.plan` → `{id, steps: [{id, title, description}]}` |
| Plan approved | `planApproved.planId` |
| Progress | `progressUpdated.title`, `progressUpdated.description` |
| Patch | `artifacts[].changeSet.gitPatch.unidiffPatch` |
| Failure | `sessionFailed.reason` |
| Completion | `sessionCompleted` |

Shell output (`bashOutput`) rarely appears.

## Gotchas

- Parse responses with `json.loads(raw, strict=False)`. They contain control characters.
- Use at most 4 parallel reads. Eight parallel reads returned 429.
- A POST that errored on read may have created the session. Search by title before retrying.
- Sessions can be visible from more than one account. Dedupe by session `name` before counting capacity.
- The API does not expose the daily counter, and it does not show a session's `automationMode` after creation.
- Over-dispatch is accepted: the session is created in `QUEUED`, not rejected.

## Count capacity per account

Reads each account's sessions with pagination and counts non-terminal states. Set the per-account concurrency limit from your plan. The script does not print keys.

```python
import json, os, urllib.parse, urllib.request
from collections import Counter

NON_TERMINAL = {"QUEUED", "PLANNING", "AWAITING_PLAN_APPROVAL",
                "AWAITING_USER_FEEDBACK", "IN_PROGRESS", "PAUSED"}
CONCURRENT_LIMIT = 15  # per account; confirm against your plan

for name in ("JULES_API_KEY", "JULES_API_KEY_2"):
    key = os.environ.get(name)
    if not key:
        continue
    token, sessions = None, []
    while True:
        url = "https://jules.googleapis.com/v1alpha/sessions?pageSize=100"
        if token:
            url += "&pageToken=" + urllib.parse.quote(token)
        req = urllib.request.Request(url, headers={"x-goog-api-key": key})
        data = json.loads(urllib.request.urlopen(req, timeout=30).read(), strict=False)
        sessions += data.get("sessions") or []
        token = data.get("nextPageToken")
        if not token:
            break
    counts = Counter(s.get("state") for s in sessions)
    used = sum(n for state, n in counts.items() if state in NON_TERMINAL)
    print(f"{name}: used={used}/{CONCURRENT_LIMIT} free={CONCURRENT_LIMIT - used} {dict(counts)}")
```

Run it with `python3 -u` from a heredoc or a file outside any downloaded directory.

## Triage AWAITING sessions

```bash
# 1. Sessions waiting on the user
curl -s -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions?pageSize=100" \
  | jq -r '.sessions[] | select(.state=="AWAITING_USER_FEEDBACK") | .name + " | " + (.title // "") + " | " + .updateTime'

# 2. Activities for one session: follow nextPageToken until it is null, then read the last agentMessaged
SID="<session-id>"
curl -s -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions/$SID/activities?pageSize=50" | jq -r '.nextPageToken'

# 3. Reply (exact payload)
curl -s -X POST -H "x-goog-api-key: $JULES_API_KEY" -H "Content-Type: application/json" \
  -d '{"prompt":"<instruction>"}' \
  "https://jules.googleapis.com/v1alpha/sessions/$SID:sendMessage"
```

Session `name` values look like `sessions/<id>`; use the `<id>` part in `$SID`.
