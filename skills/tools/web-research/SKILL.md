---
id: web-research
name: web-research
category: tools
tags:
  - web-research
goals:
  - "Use for all web research tasks - market research, competitor analysis, deep research on topics, finding information about leads/prospects, technology trends, and any inquiry requiring current web information."
authors:
  - Brahyan Belalcazar
---

# Web Research Skill

Unified web search using multiple providers for comprehensive research.

## Providers

### 1. MiniMax MCP (Primary - Recommended for most searches)
Uses MiniMax's built-in web search when available via MCP.
```javascript
// Via MiniMax MCP tool
await mcp_web_search({ query: "your question", count: 10 })
```

### 2. Brave Search API (Fast, reliable)
> API key must be provided via environment variable `BRAVE_API_KEY` (never hardcode secrets in this repo).

```javascript
const API_KEY = process.env.BRAVE_API_KEY; // or $env:BRAVE_API_KEY in PowerShell

// Web Search
GET https://api.search.brave.com/res/v1/web/search?q=query&count=10

// News Search
GET https://api.search.brave.com/res/v1/news/search?q=query&count=10

// Headers: X-Subscription-Token: $BRAVE_API_KEY
```

### 3. Tavily Search API (AI-optimized)
> API key must be provided via environment variable `TAVILY_API_KEY` (never hardcode secrets in this repo).

```javascript
const TAVILY_API_KEY = process.env.TAVILY_API_KEY;

// API Endpoint
POST https://api.tavily.com/search

// Body
{
  "api_key": TAVILY_API_KEY,
  "query": "your query",
  "max_results": 10,
  "include_answer": true,
  "include_raw_content": false
}
```

## When to Use Each

| Task | Recommended Provider |
|------|-------------------|
| Quick facts | Brave Search |
| Deep research | Tavily (with AI answer) |
| Market research | Tavily + Brave combined |
| News monitoring | Brave News |
| Company research | Tavily + Brave |
| Lead generation | Tavily (structured data) |

## Usage Examples

### Research Workflow
```javascript
// 1. Quick search with Brave
const braveResults = await braveSearch("target company");

// 2. Deep research with Tavily
const tavilyResults = await tavilySearch("industry analysis", { include_answer: true });

// 3. Combine and analyze
const fullReport = {
  quickFacts: braveResults,
  deepAnalysis: tavilyResults.answer,
  sources: tavilyResults.results
};
```

### Market Research Template
```javascript
// Research company/industry
const search = async (company, industry) => {
  const brave = await braveSearch(`${company} ${industry} news`);
  const tavily = await tavilySearch(`${company} ${industry} analysis`, {
    include_answer: true,
    max_results: 15
  });
  return { brave, tavily };
};
```

## Scripts Available

- `brave-search.js` - Brave Search CLI
- `tavily-search.js` - Tavily Search CLI
- `deep-research.js` - Combined research workflow

## Best Practices

1. **Start with Brave** for quick information
2. **Use Tavily** when you need AI-generated summary
3. **Combine both** for comprehensive research reports
4. **Check rate limits** - Brave: 2000 requests/month free, Tavily: 1000/month free
5. **Cache results** when possible to avoid重复 searches

## Notes

- Brave: Fast, good for real-time info
- Tavily: Better for AI analysis, provides structured data
- MiniMax MCP: Check if available in current session