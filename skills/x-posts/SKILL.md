---
name: x-posts
description: Draft, rewrite and check X (Twitter) posts and threads from notes, explain ranking evidence, and hand off scheduling to postmoderno when connected. Use for X writing, thread structure, character limits, links, engagement questions or reach diagnosis. Ground advice in dated sources rather than promising reach.
license: MIT
---

# Writing for X

Your job is to turn what the user wants to say into X posts that real people stop for, read to the end, reply to and send to someone. Use ranking evidence as context, while keeping the user's message and audience first; no format guarantees reach. The evidence behind every rule here is in `references/algorithm.md`; read it when the user asks how the algorithm works or questions a rule.

## What X's ranker actually rewards

X ranks each post per viewer. A model predicts how likely *that viewer* is to take each action, and a weighted sum of those predictions is the score (`home-mixer/params/param.rs`, published defaults synced 2026-10-30; experiments may differ):

| Action the viewer might take | Weight |
|---|---|
| Copy the post's link (to send it somewhere) | 20 |
| Reply · Quote · Share via DM | 5 each |
| Follow the author | 4 |
| Share | 2 |
| Repost | 1 |
| Like | 0.66 |
| Open a link in the post | 0.2 |
| Report · Mute · Not interested · Block | −234 · −59 · −52 · −31 |

Three consequences shape everything below:

1. **Write things worth sending to a specific person, or worth answering.** The copy-link prediction has a large coefficient. These are weights on predicted probabilities for a viewer, not exchange rates between actual actions; never say one share is worth a fixed number of likes.
2. **Never make a reader regret the post.** The negative weights are huge because those actions are rare; avoid content that makes people want to mute or report the author. The weights do not establish how many likes could offset an actual mute. Rage bait and bait-and-switch hooks are bad bets.
3. **Earn the read.** The model predicts dwell time and penalises "not dwelled". A teaser hook that doesn't pay off in the same post loses.

Other mechanics worth knowing:

- **The published For You pipeline filters candidates older than 48 hours.** This is not a lifetime limit on a post, and does not prove the posting hour is irrelevant.
- **Small accounts get a launch window.** An original post (not a reply or repost) from an author with ≤50k followers, younger than 2 hours and under 200 impressions, can be lifted into a viewer's top 16. Eligibility is not guaranteed distribution; make each original post complete.
- **Make the opening post complete.** The published defaults filter out-of-network replies, with a configurable exception for Phoenix-retrieved replies. Thunder normally retrieves only the early replies in a linear self-thread. These are feed-path constraints, not guarantees about every way a thread can be discovered.
- **Author diversity reduces repeated authors within one feed response.** The second post gets a multiplier of ×0.625, the third about ×0.44. This does not specify a cooldown or prove that spacing posts by a particular number of hours helps.
- **Mutuals matter.** On original posts, the reply weight jumps from 5 to 20 when author and viewer follow each other. Posts that start conversations with the people who follow you back are disproportionately strong.

## Things that get a post or account labelled as spam

X runs classifiers on new posts. Some labels limit recommendations to non-followers; others hide posts more widely. The effect depends on the label, not a generic spam verdict. These are the ones an honest writer trips by accident:

- **Asking for engagement**: "like if…", "RT to…", "follow for more", "drop a 🔥 below", "reply and I'll send you…". The engagement-baiting label is applied even to high-reputation accounts, and since July 2026 repeat offenders lose revenue sharing. A genuine, specific question about the topic is not bait ("What did you replace Zapier with?" is fine; "Thoughts? 👇" is filler at best).
- **Two or more @mentions** in one post send it through a real-time LLM spam check. Mention at most one account, and only one that would want to be tagged.
- **Near-duplicate text**, on one account or across several (X's automation rules forbid it, and a copypasta classifier clusters it). Never post the same words to two accounts or repeat last week's post; give each installment of a series fresh wording.
- **AI-slop style**: X has `llm_slop_post` and `llm_slop_user` labels; the account-level one limits reach to non-followers for 7 days. In July 2026 X removed 42,000 accounts posting "thought-leadership slop". Write like the specific person you're writing for, not like a content generator (see "Voice" below).
- **Hashtag stuffing**: hashtags have no ranking weight, and hashtag abuse is a spam category. Use none by default; one at most when it's a real community or event tag.
- **Low-quality or bad links**: X scores URL reputation. Link to reputable domains, never pin a post with a dodgy link, and don't pair a link with @mentions of strangers.

If the user's reach suddenly drops, tell them to check X's **Under the Hood** report (Settings), which shows labels limiting their account or posts, before guessing.

## Workflow

### 1. Gather what's true

Find out the one point the post must land, who it's for, and the facts you may use: numbers, names, links, media. If the postmoderno tools are connected, call `get_context` (pass the X account's id) before drafting and follow the user's saved voice, audience, guardrails and facts over the defaults in this skill.

**Never invent facts.** No made-up numbers, customers, anecdotes, quotes or results, and no first-person story the user didn't tell you. Fabricated specifics are the fastest way to embarrass the user in public. If a strong post needs a detail you don't have, ask for it, or leave a visible `[placeholder]` and say so.

### 2. Pick the format

| Use | When |
|---|---|
| **Single post** (default) | One idea. Most things. Up to 280 characters (see Counting). |
| **Single post + image** | The image carries information: a screenshot, chart, before/after, demo frame. Always write alt text. |
| **Thread** | The idea needs steps or evidence, and each part has its own payoff. Usually 3–6 posts. Put the best material early; don't rely on later replies being recommended independently. |
| **Post with link** | The click is the goal (launch, article, signup). Put the value in the text so the post is worth reading without clicking. |

**Links.** X leadership says links haven't been penalised since 2025 and that "you do not need to put the links in replies anymore" (July 2026), and no explicit link penalty was found in the reviewed scoring code. Buffer's 2026 sample found lower median engagement for links (2.25% vs 3.56% for text); this correlation does not prove why. Include the link when the click matters. Don't move it to a reply on an unsupported reach claim; reply discovery is more limited under the published defaults. A bare domain like `example.com` counts as a link too.

**Video.** In April 2026, Nikita Bier encouraged original talking-to-camera video and said reposted or aggregated media could lose impressions. Only suggest video the user can actually make.

### 3. Draft

Write 2–3 options that differ in **angle**, not in wording: for example the result, the counter-intuitive lesson, the concrete how-to. Then:

- **Line one is the payload**: the claim, the result, the surprising fact. Not a wind-up ("Let me tell you a story…"), not a teaser that withholds the point. The feed truncates; the first line decides whether anyone reads.
- **Be specific.** Real numbers from the user, real names, the exact tool, the actual mistake. Specifics are what people forward, and they are the opposite of slop.
- **Make it reply-worthy by having a position**: a clear stance someone could agree or disagree with, a trade-off made explicit, a question you actually want answered. Never ask for likes, reposts, follows or replies.
- **One idea per post.** In a thread, each post should make sense if it's the only one someone sees.
- **Cut.** Remove every word that doesn't change the meaning. Short lines and white space for scanning, but no one-word-per-line drama.

### 4. Voice: don't sound like a model

Use the user's own register: their vocabulary, their sentence length, their level of formality. Avoid the patterns readers now recognise as machine-written:

- Stock openers and closers: "Here's the thing", "Let's dive in", "In today's fast-paced world", "Game-changer", "Unlock", "This is huge", "Read that again", "🧵👇".
- Constructions: "It's not X, it's Y", tricolons added for rhythm, a closing moral after every post, em-dash chains, rhetorical questions answered immediately.
- Decoration: emoji bullets, ✅/🚀/🔥 sprinkles, all-caps emphasis, hashtags at the end.

A post that sounds like the user on a good day beats a "perfect" post that sounds like everyone else's AI.

### 5. Check before showing

Run `python3 scripts/check_x_post.py` from this skill's folder (or use its absolute path) on the drafts: pass them on stdin, separate the posts of a thread with a line containing only `---`, and separate alternative options with a line containing only `===`. It estimates X's weighted length for each post and flags links, mentions, hashtags, bait phrases, common AI tells and thread problems. Treat its flags as prompts to look again, not verdicts. The helper is dependency-free, not the full twitter-text parser: rare URL suffixes and emoji sequences can differ. For exact validation, use X's composer or the official twitter-text library, especially near 280. If you can't run scripts, estimate by the rules below and label the count as estimated. Then ask yourself:

- Would someone send this to a friend, or reply with their own experience?
- Does the first line deliver, without needing the rest?
- Is every fact one the user gave you?
- Would the user say this, in these words?

Show the user the final drafts with each post's estimated weighted length, and say which option you'd pick and why in one line.

### Counting characters

X counts a *weighted* length, limit 280 (Premium accounts can post longer, but keep to 280 unless the user says they have Premium and is posting natively):

- Most Latin, Cyrillic, Greek, Arabic and Hebrew characters, plus curly quotes and dashes, count **1**.
- Each emoji, CJK character, and most symbols (… → ★) count **2**.
- Every URL X recognises counts **23**, however long or short. Text is normalised to NFC first.

See [X's counting documentation](https://docs.x.com/fundamentals/counting-characters) for the authoritative rules; the helper checks draft text, not platform acceptance.

## Scheduling through postmoderno

If postmoderno tools are available and the user wants to post or schedule, read `references/postmoderno.md` for the hand-off: drafts, threads as replies, previewing, confirming, and what a link costs. The user must see the preview and say yes before anything is scheduled.

## When the user asks about the algorithm

Answer from `references/algorithm.md`, which separates what the code shows, what X has said, and what is only folklore. Don't repeat popular numbers that aren't true anymore ("a reply is worth 27 likes", "links get 50% less reach", "Premium is a 4x boost", "the first 30 minutes decide everything"), and say plainly when nobody knows.
