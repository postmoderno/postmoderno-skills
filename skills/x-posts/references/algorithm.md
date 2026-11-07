# How X's For You ranking works (evidence)

Sources, in order of trust:

1. **Code**: the open-sourced For You algorithm, [xai-org/x-algorithm](https://github.com/xai-org/x-algorithm/tree/3b6919f87532e57063bb3f1e85c2f509323b513e), commit `3b6919f87532e57063bb3f1e85c2f509323b513e` (2026-11-07). Paths below are relative to that snapshot. The published defaults can differ from experiments or later production settings.
2. **Statements**: what X staff said publicly, with dates.
3. **Data studies**: large third-party samples (Buffer, Sprout, Metricool). These show correlation, not cause.

Anything not listed here is unknown. Say so rather than fill the gap with folklore.

## Contents

- Scoring
- Time and attention
- Adjustments after scoring
- Threads and replies
- Filters and spam labels
- Links
- Media, hashtags, mentions
- Premium and reputation
- Timing and frequency
- Scheduling tools and the API
- Diagnosing a reach drop
- Do not claim

## Scoring

Phoenix, a transformer, reads the viewer's recent engagement history and predicts, for each candidate post, the probability of each action (`xai-value-model/phoenix_scores.rs`). `RankingScorer` computes `score = Σ weight × P(action)` (`xai-value-model/scoring.rs`).

Weights (`home-mixer/params/param.rs:404-533`, synced 2026-11-06):

| Action | Weight |
|---|---|
| share_via_copy_link | 20.0 |
| reply | 5.0 (20.0 on original posts between mutual follows) |
| quote | 5.0 |
| share_via_dm | 5.0 |
| follow_author | 4.0 |
| share | 2.118 |
| retweet | 1.0 |
| favorite (like) | 0.708 |
| cont_click_dwell_time | 0.385 |
| click | 0.274 |
| open_link | 0.2 |
| dwell (probability) | 0.05 |
| photo_expand | 0.05 |
| quoted_click | 0.05 |
| post_unexplored | 0.015 (in-network posts only by default) |
| cont_dwell_time | 0.0075 |
| video_open, video quality view, profile click | 0 |
| not_dwelled | −0.02 |
| block_author | −31.2 |
| not_interested | −53.07 |
| mute_author | −58.8 |
| report | −234 |

How to read them (the repo's own warning, `README.md`): weights multiply the *predicted probability for this viewer*, not raw counts. "One report cancels 468 likes" is wrong; reports are weighted high because they are more than 1000× rarer than likes. Engagement only trains ranking when it happens on a post served in the Home timeline, so coordinated "go like this" raids from a group chat have no ranking effect (`param.rs:399-403`).

`cont_click_dwell_time` and `cont_dwell_time` multiply a predicted amount of time instead of a probability, so don't compare them with the other rows.

X retunes these values. The main changes between the first published weights (2026-08-13) and the 2026-11-06 sync: like 0.5 → 0.708, not interested −43.2 → −53.07, click 0.4 → 0.274, share 2.0 → 2.118, dwell 0 → 0.05, cont_click_dwell_time 0 → 0.385, cont_dwell_time 0.004 → 0.0075, video open 0.05 → 0 (it was 0.02 before the 2026-11-05 change). Copy link, reply, quote, DM, follow, repost and report held still. Check the file before quoting a number.

Bookmarks are a training label but carry **no weight** in the score.

## Time and attention

- Dwell time is predicted with thresholds from 2 s to 120 s on Home (`phoenix/xrex/models/loss_recsys.py`, update 2026-10-08). Click-dwell counts when it exceeds 10 s.
- Since 2026-10-13, retrieval (which out-of-network posts are even considered) is also trained on posts people "read all the way through".
- Post length, line breaks, links and media count are passed to the model as features, but nothing in the repo shows a fixed rule like "longer is better". Length helps only when it holds attention.

## Adjustments after scoring

The author diversity and out-of-network values below are defaults in `vm-ranker/params.rs`, which doesn't follow the synced file: it still lists the like at 0.5. Treat them as approximate.

- **Author diversity** (`vm-ranker/params.rs:175-192`): the k-th extra post from the same author in one response is multiplied by `0.75·0.5^k + 0.25`, giving ×1, ×0.625, ×0.44, ×0.34 and never below ×0.25.
- **Out-of-network discount**: ×0.75 for posts from accounts the viewer doesn't follow, and also for replies and reposts from accounts they do follow.
- **New-author boost** (`author_cold_start.rs`, `param.rs:608-687`): an original post, from an author with ≤50,000 followers, ≤2 h old, with fewer than 200 home impressions, can take on the score of the post in position 16. One per feed request: X samples a reward from each eligible post's likes per Home view, keeps the top two samples, and lifts whichever of those has the higher ranking score. The post must already rank within the top 97% of scored candidates (`LowImpressionsMaxPositionRatio`), and experiment arms can limit which authors qualify for some viewers; by default every viewer is in the open holdout. In the published defaults the out-of-network and author multipliers apply after the lift (`xai-value-model/scoring.rs`), so a lifted out-of-network post can land lower.
- **Diversity rerank** (`vm-ranker/`): the top 150 are reordered so posts with similar embeddings aren't stacked together.
- **Debias**: `VMRankerSendDebiasInputs` has been true since 2026-10-27, but `UserDebiasEnabled` reads false in the lagging `vm-ranker/params.rs`. Whether this step runs is unknown.

## Threads and replies

- By default, out-of-network replies and reposts are filtered out of this For You pipeline (`home-mixer/filters/oon_retweet_reply_filter.rs`). `EnablePhoenixOonReplies` can allow Phoenix-retrieved replies through; its published default is false. This does not constrain discovery through conversations, profiles, search, quotes or other paths.
- For followers, Thunder returns a self-reply only when it answers the root, or answers a reply to the root (`thunder/posts/post_store.rs:341-364`). For a linear self-thread with available ancestors and a nonempty following list, this path normally retrieves only the first two self-replies. Do not generalise that to all candidate sources or branched conversations.
- `DedupConversationFilter` keeps only the highest-scoring post per conversation. A shown reply appears as a module: root, one middle post, and the reply.

## Filters and spam labels

- **Age**: the Phoenix candidate pipeline drops posts older than 48 h (`home-mixer/params/config.rs:39`, `home-mixer/candidate_pipeline/phoenix_candidate_pipeline.rs`). This is a feed filter, not post expiration.
- Already seen, already served, muted keywords, blocked or muted authors, and subscriber-only posts the viewer can't access are all filtered out.
- **Scoring cap**: X scores at most 2,800 posts per request (`PhoenixScoresResultSize`). Since 2026-10-22 `EnableFairShareRanking` trims every source by the same share when candidates exceed the cap.
- **Visibility labels**: for out-of-network recommendations, posts labelled SpamHighRecall, MaliciousUrl or DoNotAmplify are dropped, as are posts by authors with those labels (`visibility-filtering/rules/levels.rs`). Followers still see them. Posts labelled SPAM are dropped for everyone but the author.

What triggers labels:

| Trigger | Label | Source |
|---|---|---|
| Engagement baiting / farming (Grok classifier) | post SpamHighRecall, **even for high-reputation accounts** | `grox/flows/ptos/task_write_safety_post_annotations_result_sink.py:233-248` |
| ≥2 distinct accounts mentioned in the text or tagged in media | sends it to a real-time LLM spam check | `grox/flows/ptos/task_filter.py:37-67` |
| `llm_slop_post` | post RiskyHighVizReply, 30 days | `abuse-enforcement-service/service-lib/rules/enforcement_post.yaml:39-44` |
| `llm_slop_user` | account SpamHighRecall, 7 days | `enforcement_user.yaml:118-123` |
| Gibberish, fast reply spam | post SpamHighRecall, 30 days | `enforcement_post.yaml` |
| Near-duplicate text clusters | COPYPASTA_SPAM | `botmaker-rules/…/BBQDuplicateTextProd.bot` |
| Bad URL / low-quality URL | SPAM / SpamHighRecall | `botmaker-rules/…Bad_URL_Sources.bot`, `LQ_…_v2.bot` |
| Low-quality URL + @mention of a non-follower | SpamHighRecall | `LQ_…NonFollower.bot` |
| Pinning a post with a bad link | account SpamHighRecall, 1 week | `PinnedLowQualityOrBadUrl.bot` |
| High spam-reports-per-like history | every new post AGATHA_SPAM, 1 week | `agatha/` rules |
| Mechanical posting cadence | modelled by the `bdsm` bot detector; thresholds redacted | `bdsm/README.md` |

High-reputation accounts (user-cred ≥54, roughly PageRank over follows and recent likes and reposts) are exempt from most rule-based spam labels, but not from the engagement-bait ones.

Statements:

- Since 2026-07-16 X uses Grok to detect accounts that solicit engagement; three strikes means removal from revenue sharing and possible suspension (Social Media Today, 2026-07-16).
- ~2026-07-24: X removed ~42,000 chatbot reply accounts "spamming thought-leadership slop about artificial intelligence" (Nikita Bier).
- X's automation rules forbid "duplicative or substantially similar" posts on one account or across accounts (help.x.com, X automation rules, updated April 2026).

## Links

- **Code**: no explicit link penalty found in the reviewed scoring code; this does not establish every production effect. `open_link` is +0.2. Links are judged by URL reputation labels (above).
- **Statements**: Musk, ~2025-04-25: no explicit rule limits links, but links that cut time on X naturally get less exposure; summarise the content in the post. Bier, 2026-07-28: "you do not need to put the links in replies anymore." Musk, 2026-07-29: "We haven't [penalised links] for over a year."
- **Data**: Buffer 2026 median engagement rate: text 3.56%, image 3.40%, video 2.96%, link 2.25% (published 2026-03-19). No controlled test after July 2026, and no data showing link-in-reply beats link-in-post.
- **Practical**: X turns bare domains (`example.com`) into links too. In the current postmoderno product configuration, a link post uses about 13 plain posts' worth of X allowance. That is a product estimate, not an immutable X tariff; the actual preview is authoritative.

## Media, hashtags, mentions

- Media weights are small (photo expand 0.05; video open and video quality view 0, with video open dropping from 0.02 on 2026-11-05). A video must be over 10 s to count as a quality view.
- Bier (2026-04-13) encouraged original talking-to-camera video and said reposted or aggregated content can lose up to 90% of impressions.
- Hashtags: no ranking weight; hashtag abuse is a spam category. Musk (2024-12): "please stop using hashtags."
- Polls, GIFs, emoji: no evidence either way.

## Premium and reputation

- No Premium ranking multiplier in the code. Premium accounts get a share of the PageRank "teleport" mass in user-cred (`user-cred-v2/`), which raises reputation and exempts more spam rules. That can protect reach to non-followers indirectly, though Premium doesn't guarantee the reputation. A separate reply-ranking model reads verified status as an input (`phoenix/xrex/models/recsys_reply_two_tower_v2_model.py`).
- X's help page lists reply prioritisation by tier.
- Buffer (2025-10, 18.8M posts) saw about 10× median impressions for Premium accounts. This is observational: committed creators buy Premium. Don't present it as a guaranteed boost.

## Timing and frequency

- Buffer (8.7M posts, 2026-03): best slot Tuesday 9 am, then 10–11 am. Sprout (2026-03): Tue–Thu, 12–6 pm local time. They disagree on the hour and agree that Saturday is weakest. The account's own analytics beat both.
- Frequency: no X study. Bier (2026-01): "every post consumes part of your daily audience reach." The author-diversity decay above is within one feed response; it does not prove a daily reach budget or a minimum posting interval.

## Scheduling tools and the API

- No field in the ranking code holds the app that created a post. `client_app_id` in `home-mixer` is the viewer's app, and Phoenix uses it for iOS and Android metrics.
- The posting app does reach two abuse systems. The `bdsm` bot detector takes it as an input feature (`bdsm/rust/abuse-v3-features/src/lib.rs:188-194`), and BotMaker receives it as `applicationId` (`botmaker/scarecrow_features/src/main/java/com/twitter/scarecrow/features/FeaturesOfTweet.java:66-67`). No published rule uses that field, but X withholds some rules and redacted the `bdsm` thresholds.
- There is no evidence that scheduled or API posts get less reach, and none that they are guaranteed safe.
- Cadence features are not evidence that minute-level timing jitter avoids detection or improves reach. Honour the user's chosen schedule.
- [X's Manage Posts documentation](https://docs.x.com/x-api/posts/manage-tweets/introduction), checked 2026-10-31, says self-serve replies require the original author to have mentioned or quoted the replying account. It does not clarify self-thread exemptions. postmoderno has since verified that its scheduled self-threads publish (reported 2026-11-02); other API clients may differ.

## Diagnosing a reach drop

X's [**Under the Hood**](https://x.com/i/jf/under_the_hood) report shows the labels limiting an account or its posts, and since 2026-09 any government-required limits. It is a pilot for a small group, and needs an account at least a year old with 10 or more posts in the prior month.

## Do not claim

- Specific penalty or boost percentages: "links lose 30–50%", "94% fewer views", "Premium gives 4×/10×", "hashtags add 21%".
- Old weights: "a reply is worth 27 likes", "an author reply-back is worth 150 likes" (2023-era code).
- "Put the link in the first reply to avoid the penalty."
- One best posting time.
- "The first 30 or 60 minutes decide everything."
- "Grok rewards positive tone" or "penalises negativity" (vendor claims, no official source).
- Threads beat long posts, or the reverse (no credible 2026 data).
- Scheduled or API posts lose reach, or are proven safe.
- AI-assisted text is down-ranked as such. The labels target slop *patterns* and spam behaviour, not tool use.

## Source links

The code paths above refer to the pinned snapshot, rather than floating `main`. Key entry points:

- [Scoring defaults and probability caveat](https://github.com/xai-org/x-algorithm/blob/3b6919f87532e57063bb3f1e85c2f509323b513e/home-mixer/params/param.rs#L375).
- [Reply filtering and configurable exception](https://github.com/xai-org/x-algorithm/blob/3b6919f87532e57063bb3f1e85c2f509323b513e/home-mixer/filters/oon_retweet_reply_filter.rs).
- [Thunder reply retrieval](https://github.com/xai-org/x-algorithm/blob/3b6919f87532e57063bb3f1e85c2f509323b513e/thunder/posts/post_store.rs#L330).
- [Author diversity parameters](https://github.com/xai-org/x-algorithm/blob/3b6919f87532e57063bb3f1e85c2f509323b513e/vm-ranker/params.rs#L175).
- [Posting app passed to BotMaker](https://github.com/xai-org/x-algorithm/blob/3b6919f87532e57063bb3f1e85c2f509323b513e/botmaker/scarecrow_features/src/main/java/com/twitter/scarecrow/features/FeaturesOfTweet.java#L66).

Web sources (statements are attributed claims, studies are observational):

- [X automation rules](https://help.x.com/en/rules-and-policies/x-automation), updated April 2026; duplicate and automated-content rules.
- [X character counting](https://docs.x.com/fundamentals/counting-characters) and [twitter-text](https://github.com/twitter/twitter-text); NFC, weighting, emoji and URLs.
- [July link-handling statements, reported by PPC Land](https://ppc.land/x-drops-year-old-link-penalty-musk-tells-zuckerberg-on-platform/), 2026-07-30.
- [Musk's earlier link statement](https://x.com/elonmusk/status/1915806794393457034), April 2025.
- [Buffer content-format study](https://buffer.com/resources/data-best-content-format-social-media/), 2026-03-19; the X section reports 3.56% text and 2.25% link median engagement.
- [Engagement-bait enforcement, reported by Social Media Today](https://www.socialmediatoday.com/news/x-updates-its-engagement-bait-detection/825495/), 2026-07-16.
- [Bier's account-removal statements](https://x.com/nikitabier/status/2080747924380856519) and [follow-up](https://x.com/nikitabier/status/2081111047340167485), July 2026.
- [Original video comments, reported by PiunikaWeb](https://piunikaweb.com/2026/04/13/x-twitter-original-talking-videos-nikita-bier/), 2026-04-13.
- [Hashtag comments, reported by Social Media Today](https://www.socialmediatoday.com/news/do-you-still-need-to-use-hashtags/735983/), 2024-12-17; dated opinion, not an experiment.
- [X Premium features](https://help.x.com/en/using-x/x-premium) and [Buffer Premium study](https://buffer.com/resources/x-premium-review/), 2025-10-02.
- Timing: [Buffer](https://buffer.com/resources/best-time-to-post-on-twitter/), 2026-03-13, and [Sprout](https://sproutsocial.com/insights/best-times-to-post-on-twitter/), March 2026.
- [Bier's daily-reach remark, reported by ForkLog](https://forklog.com/en/?p=93020), 2026-01-12; secondhand, since deleted.

Recheck dated claims before presenting them as current rules. Code defaults, staff statements and observational results do not by themselves prove a causal writing tactic.
