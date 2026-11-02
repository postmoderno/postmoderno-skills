# Posting and scheduling through postmoderno

Use this when the postmoderno tools are connected and the user wants a post to go out. Talk to the user in plain words ("your X account", "Tuesday 9:00 your time"). Don't show them ids, tool names or JSON.

## Before drafting

1. `get_briefing` once at the start of a session, to see connection problems, idle drafts and warnings.
2. `list_accounts` to find the user's X account(s). If none is connected, tell them to connect X on the postmoderno site; you can still draft.
3. `get_context` with that account's id. Its voice, audience, guardrails and facts override this skill's defaults. When the user corrects your tone in a way worth keeping ("never use emoji", "I say 'folks', not 'guys'"), offer to save it with `set_context` so every future session knows it.
4. For a recurring series, `next_in_series` gives the number, the user's format and the previous installment. Write fresh wording each time, because near-duplicate posts get labelled as spam.

## Creating the draft

- **Single post**: `create_post` with the body and the X account id in `target_account_ids`. Generate one `idempotency_key` per distinct creation and reuse it unchanged only on retries of that same call.
- **Thread**: `create_post` for the first post, then `add_reply` once per further post, in order, each with its own idempotency key. Each reply goes out `delay_sec` after the one before it publishes (default 60 seconds), which is fine for threads. postmoderno has verified that scheduled X threads publish this way.
- **Images**: pass public image URLs with alt text in `media`, or use `create_upload_url` for a local file, before scheduling. Always write alt text.
- Keep X posts within **280 weighted characters**. postmoderno validates X’s weighted length: recognised URLs count as 23, emoji sequences and CJK characters as 2, and text is normalised to NFC before counting. Premium does not bypass this product limit.
- **One X account per post.** If the user targets two X accounts with the same text, warn them: X's automation rules forbid identical or near-identical posts across accounts. Offer a rewritten version for the second account. Posting the same idea to LinkedIn or another platform is fine.

## Preview, confirm, schedule

1. Call `preview_schedule` with the post and the proposed time ("now" or a time in the user's timezone). If replies were already saved using `add_reply`, omit the optional `replies` argument and preview the stored chain. If using inline proposed replies instead, pass that exact array through both preview and schedule; do not mix the two approaches.
2. Show the user what it returns: the local and UTC time, which account, how many posts in the chain, what it will use from their plan or wallet, and any blockers or warnings, or that there are none.
3. Wait for an explicit yes. The preview is a snapshot, not permission.
4. Call `schedule_post` with exactly that input and the returned `preview_revision`. If the draft, time or chain changed, the revision is rejected: preview again and ask again.

## What X posts cost the user

On X, a post containing a link (bare domains like `example.com` count) uses about 13 plain posts' worth of the X allowance, because X charges the publisher that much more. This is the current product estimate, not a fixed X tariff; use the preview's actual allowance or wallet projection when it differs. When a draft has a link, tell the user in posts, never dollars ("this one uses about 13 posts of your X allowance because of the link"), and let them choose. If the link isn't the point of the post, offer a version without it.

## Timing

- Spread a batch across the day when that suits the audience. Author-diversity decay applies within one feed response; it does not establish a minimum interval between posts.
- Weekday slots in the audience's timezone are a reasonable default; Saturday is weakest in 2026 data. If the user has their own analytics, use those.
- Honour the user's requested schedule. No controlled evidence here shows that minute-level timing jitter improves reach or avoids spam labels.

## When something goes wrong

If a tool returns an error, read its `message` and `next_action` and tell the user plainly. Never say a post went out unless the tool's status says so. Use `diagnose` when the briefing reports trouble or a post didn't appear. Retry only when `retryable` is true, preserving the original idempotency key. If a named tool is missing, explain that the connection may lack permission; never claim it was called.
