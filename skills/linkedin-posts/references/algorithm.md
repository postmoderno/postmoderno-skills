# LinkedIn feed evidence

Reviewed 2026-10-31. Scope: organic feed posts, not ads, job recommendations or profile-search ranking. Use this reference for ranking questions and whenever a writing recommendation depends on an algorithm claim.

## What is public

The research found substantial first-party engineering material, but no official release of the complete current feed code, trained models and production scoring weights comparable to X's repository. This is a bounded research finding, not proof that no additional code exists.

[Photon ML](https://github.com/linkedin/photon-ml) is public LinkedIn code for training GLM/GLMix models, with historical adoption in feed ranking among other products. It is not a reproducible release of the current deployed feed. [LiRank (2024)](https://arxiv.org/abs/2402.06859) is useful background research, not an interchangeable specification for every feed version.

## Current ranking research

**Lars Hertel, Gaurav Srivastava and colleagues: Feed Sequential Recommender (Feed SR).** First submitted 2026-02-12; latest version reviewed 2026-09-16.

- [Paper and full author list](https://arxiv.org/abs/2602.12354)
- [Version 3 full text](https://arxiv.org/html/2602.12354v3), especially sections 3, 4 and 6.

The paper reports serving most feed traffic. It describes predicting actions such as long dwell, likes, comments and reshares from a viewer's interaction history, combining predictions with an objective, then applying further business logic. Candidate popularity and viewer-author affinity remain relevant context features.

This supports personalized relevance, not a fixed recipe for every creator. A model feature's existence does not reveal its effect on one post. The paper does not supply a usable table of current like/comment exchange rates, and model A/B improvements are not promised gains for a writer following this skill.

## Semantic retrieval and professional context

**Hristo Danchev, 2026-03-12:** [Engineering the next generation of LinkedIn's Feed](https://www.linkedin.com/blog/engineering/feed/engineering-the-next-generation-of-linkedins-feed).

The account describes LLM-derived representations for members and posts, including professional context, post text and engagement history, followed by sequential ranking. Relevant posts can be discovered beyond an author's followers. Matching is semantic, rather than simply a quota of exact keywords.

Editorial inference: identify a professional reader and make the topic and usefulness clear. This does not prove that creators must stay in one niche forever, repeat keywords, or update their headline to obtain a guaranteed boost.

The March overview and September paper describe different architecture details. Treat them as dated accounts of an evolving system, not a single timeless formula.

## Reading, skipping and dwell time

**Fengyu Zhang, Mohit Kothari and Birjodh Singh Tiwana, 2024-10-01:** [Leveraging Dwell Time to Improve Member Experiences on the LinkedIn Feed](https://www.linkedin.com/blog/engineering/feed/leveraging-dwell-time-to-improve-member-experiences-on-the-linkedin-feed).

The work describes skip prediction and positive long-dwell modeling. A universal fixed long-dwell threshold performed inadequately; the system normalized thresholds by attributes including content type, creator type and distribution method, updating them from observed data.

The 2026 Feed SR paper also describes long dwell as an objective with a threshold dependent on post type. Neither source establishes a universal "15-second" or "30-second" writing rule, a word-count target, or that padding a post improves reach.

Editorial inference: deliver useful substance worth reading and avoid bait that fails to pay off. Longer is not automatically better. Quiet readers matter even when they do not react.

Earlier foundation: **Siddharth Dangi and colleagues, 2020-05-12**, [Understanding dwell time to improve LinkedIn feed ranking](https://www.linkedin.com/blog/engineering/feed/understanding-feed-dwell-time). Treat its implementation details as historical.

## Authenticity and engagement manipulation

**LinkedIn newsroom, 2026-03-12:** [How LinkedIn Is Improving the Feed to Show More Relevant, Authentic Professional Content](https://news.linkedin.com/2026/ImprovingTheFeed).

LinkedIn explicitly describes reducing repetitive low-substance posts, engagement bait, automated comments and engagement pods. Examples include prompts asking for agreement and videos unrelated to their text.

**Oscar Rodriguez, published 2025-09-05:** [LinkedIn: Where Real Conversations Matter](https://www.linkedin.com/pulse/linkedin-where-real-conversations-matter-oscar-rodriguez-ejwee/).

This firsthand account describes detecting coordinated boosting, limiting artificially boosted distribution and acting against tools that manufacture engagement.

These statements support avoiding inauthentic engagement. They do not establish that any AI-assisted draft is forbidden, that every common phrase triggers a classifier, or that approved scheduling has the same treatment as comment automation. Do not promise either immunity from enforcement or a reach penalty based solely on the writing tool used.

## Professional relevance and observation

**Tim Jurka, published 2025-08-11:** [How Does the LinkedIn Feed Work?](https://www.linkedin.com/pulse/how-does-linkedin-feed-work-tim-jurka-oxraf).

Jurka says he has worked on the feed for over a decade. He describes professional identity, contextual relevance and personalized distribution beyond followers, and recommends examining one's own posting patterns by topic, format and timing. The article reader reported a 2026-05-15 update; metadata alone does not identify what changed.

**Sakshi Jain, 2025-11-20:** [Putting members first: testing and measuring how content appears in your Feed](https://www.linkedin.com/blog/engineering/feed/putting-members-first-testing-and-measuring-how-content-appears-in-your-feed).

This explains why superficially similar posts can receive different engagement under many signals. Its statement that demographics are not used directly to set visibility is LinkedIn's stated policy, not proof that every indirect bias has been eliminated.

Editorial inference: use account observations to form hypotheses, compare similar goals and conditions, and measure useful outcomes. Do not turn a single comparison into a causal claim.

## Do not claim without additional evidence

The sources reviewed do not establish:

- A universal external-link penalty or a guaranteed benefit from hiding the link in the first comment.
- Fixed engagement weights, or that an actual comment is worth a specific number of likes.
- A first-hour distribution cutoff, or that a post cannot be discovered later.
- A universal word count, required number of line breaks, hashtag formula or best posting time.
- A guaranteed boost for documents, video, verification, Premium or a particular scheduling method.
- A numeric penalty for every AI-assisted post, or that human assistance is a reliable classifier-evasion method.

Lack of verification is not proof that a factor has no effect. If a user provides a newer source, check its date, scope and methods before updating the advice. Keep engineering mechanisms, platform statements, observational studies and editorial judgments distinct.
