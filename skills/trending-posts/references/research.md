# Researching with treg

treg's catalog changes every week, so search by the job and read the current entry. Do not rely on a remembered tool id. Observations below are dated 2026-11-04.

## The loop

| Step | MCP tool | CLI |
|---|---|---|
| Find a tool for a job | `catalog_search` | `treg catalog search "<job>"` |
| Read parameters and price | `catalog_get` | `treg catalog get <id>` |
| Call it | `call` | `treg call <id> --data '{...}'` |

Prefer a routed `treg.*` tool when one exists: treg picks the provider and falls back when one fails. Over the CLI, cap a routed call with the header `X-Treg-Route-Max-Cost`. Routed tools list no fixed price, because a fallback can cost more, so over MCP call the direct provider endpoint whose price `catalog_get` shows when cost matters.

## Where to look

| To learn | Search the catalog for | What to expect |
|---|---|---|
| What developers are discussing | `hacker news front page` | The strongest signal for technical readers. Points and comment counts show real interest. |
| What a community is discussing | `reddit search results`, with a subreddit | Clean rows with a title, link and date. Pick subreddits the reader uses. |
| What people say about a topic | `search x posts` | Newest posts first, mixed languages. Filter by language and read it for reactions, because recency says nothing about popularity. |
| What professionals are saying | `search linkedin posts` | Useful when the post is for LinkedIn. |
| What the press covers | `search recent news` | Results can be weeks old, and many are tutorials. Check the date on each one. |
| Whether interest is rising | `google trends` | Slower signal. Use it to compare two subjects. |

Skip national trending lists for a niche reader. On 2026-11-04 the US list from `x trending topics by country` was election politics from top to bottom.

If a call returns rows with no titles, or a shape you can't read, try another provider of the same job through `catalog_get` before dropping the source. The routed subreddit feed did this on 2026-11-04, while the Reddit search tool returned clean rows.

## Cost

Tools charge per call, at listed prices. One test pass on 2026-11-04 made five calls (Hacker News, a subreddit, X search, news, national trends) and cost $0.0027 in total. Read the price with `catalog_get`, because prices change and a routed call can cost more when it falls back.

Say the price before any call that costs more than a cent, as treg asks. Google Trends cost $0.011 a call on 2026-11-07, four times the whole test pass. Cheaper calls can run without asking. Report each charge. It appears as `cost_usd` over MCP, and in the `X-Treg-Cost-Micro` header or the CLI's `charged` line otherwise. Before a loop over many inputs or any generation task, tell the user the expected total and stop before you pass what they agreed to.

## Errors

- A provider's 4xx other than 429 means your request is wrong: fix it instead of switching provider.
- After a 429 or 5xx, try the next provider of that job and say which one you used.
- When an answer or error names a next step, follow it.
- A job with no tool (`verdict: none`): file it with `catalog_request` instead of rephrasing the search.
