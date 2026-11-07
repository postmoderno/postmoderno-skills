# postmoderno skills

Agent skills for writing social posts grounded in platform ranking evidence, and for scheduling them with [postmoderno](https://postmoderno.io).

Each skill works on its own in any agent that reads the Agent Skills format (a folder with a `SKILL.md`). When the postmoderno connector is also installed, the skill uses your saved voice and can schedule the result after you confirm a preview.

## Skills

| Skill | What it does |
|---|---|
| [`x-posts`](skills/x-posts/SKILL.md) | Writes X posts and threads from your notes, estimates their X weighted character count and spam patterns, and explains how X ranks posts. Built on X's open-sourced For You code ([xai-org/x-algorithm](https://github.com/xai-org/x-algorithm), November 2026) and on 2026 statements and data, with sources in [`references/algorithm.md`](skills/x-posts/references/algorithm.md). |
| [`linkedin-posts`](skills/linkedin-posts/SKILL.md) | Drafts and rewrites professional feed posts from your facts and voice, explains ranking evidence from LinkedIn engineers, and hands supported posts to postmoderno for confirmed scheduling. Sources and limits are in its [algorithm reference](skills/linkedin-posts/references/algorithm.md) and [postmoderno hand-off](skills/linkedin-posts/references/postmoderno.md). |
| [`trending-posts`](skills/trending-posts/SKILL.md) | Finds what your audience is discussing today, checks the claim at its source, and turns one topic into an X or LinkedIn post. Uses [treg](https://treg.to) for live research, billed per call, and postmoderno for scheduling. Sources and costs are in its [research guide](skills/trending-posts/references/research.md). |

The skills don't make up facts, numbers or stories for you. If a post needs a detail you didn't give, the agent asks or leaves a visible placeholder.

## Install

**Claude Code**

```
/plugin marketplace add postmoderno/postmoderno-skills
/plugin install postmoderno@postmoderno-skills
```

**Claude apps (claude.ai, desktop)**

Zip the folder for each skill you want and upload it under Settings → Capabilities → Skills:

```
git clone https://github.com/postmoderno/postmoderno-skills
cd postmoderno-skills/skills
zip -r x-posts.zip x-posts
zip -r linkedin-posts.zip linkedin-posts
zip -r trending-posts.zip trending-posts
```

**Other agents**

Copy any folder under `skills/` into the folder your agent loads skills from.

## Scheduling with postmoderno

To have the agent schedule what it writes, add postmoderno as a connector with the URL `https://mcp.postmoderno.io/mcp` and sign in at [postmoderno.io](https://postmoderno.io). The agent shows you a preview of each post (account, time, cost) and schedules it only after you say yes.

## Research with treg

`trending-posts` reads live data through [treg](https://treg.to). Add `https://treg.to/mcp/` as a connector, or install the CLI from [treg.to/llms.txt](https://treg.to/llms.txt). treg bills per call from your own prepaid balance, and the agent reports what each run cost.

## Keeping it current

Social platforms change their ranking often. Dated facts live in each skill's `references/` folder, so updates touch those files rather than the instructions. Corrections with a source are welcome as issues or pull requests.

## Development

Python 3 is enough for the X draft checker and its regression tests:

```sh
python3 -m unittest discover -s tests -v
python3 skills/x-posts/scripts/check_x_post.py drafts.txt --json
claude plugin validate . --profile directory
```

The checker is an estimate, not a complete twitter-text implementation. Use X's composer or the official library for exact URL and emoji edge cases.

## License

[MIT](LICENSE).
