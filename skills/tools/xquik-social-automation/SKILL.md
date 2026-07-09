---
id: xquik-social-automation
name: Xquik Social Automation
category: tools
tags:
  - xquik
  - mcp
  - x-twitter
  - social-media
  - automation
goals:
  - "Use Xquik as an API or MCP source for X/Twitter search, analytics, monitoring, and approval-gated publishing."
  - "Keep agent workflows explicit about credentials, approval boundaries, and output validation before acting on social data."
authors:
  - Xquik
license: MIT
original_source: https://github.com/Xquik-dev/hermes-tweet
---

# Xquik Social Automation

Use this skill when an agent needs public X/Twitter context, account monitoring,
tweet analytics, webhook-backed events, or approval-gated publishing through
Xquik.

## When To Use

- Research public X/Twitter posts before drafting, scoring, or scheduling.
- Pull reviewed tweet, follower, style, trend, or monitor data into a report.
- Connect a host that supports remote MCP servers to `https://xquik.com/mcp`.
- Keep final publish actions behind an explicit user approval step.

## Setup

1. Create an API key in the Xquik dashboard.
2. Store it as `XQUIK_API_KEY` in the host environment.
3. Configure the remote MCP endpoint with an authorization header:

```json
{
  "servers": {
    "xquik": {
      "type": "http",
      "url": "https://xquik.com/mcp",
      "headers": {
        "Authorization": "Bearer ${XQUIK_API_KEY}"
      }
    }
  }
}
```

## Workflow

1. Ask what social source, account, keyword, or monitor the user wants to use.
2. Read data through Xquik and keep the raw result available for review.
3. Summarize source limits, timestamps, and any missing fields.
4. Draft recommendations separately from any write action.
5. Request explicit approval before scheduling, publishing, or replying.

## Safety

- Do not print, log, commit, or paste API keys.
- Do not infer private account data from public results.
- Do not publish, reply, follow, or message without explicit user approval.
- Prefer links, IDs, timestamps, and compact evidence tables over broad claims.
