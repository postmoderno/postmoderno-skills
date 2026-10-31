# LinkedIn through postmoderno

Use this reference when postmoderno is connected, including when loading saved account context before drafting. Explain actions in plain language; account IDs and tool arguments are for calls, not the user's post.

## Context without unnecessary writes

1. Call `get_briefing` once at the start of the planning or drafting session. Follow relevant connection warnings; a suggestion is not authorization to change anything.
2. Use `list_accounts` to identify the intended LinkedIn account, and `list_platforms` when current capabilities or limits are unclear. If the publisher is ambiguous, resolve it before saving or scheduling.
3. Call `get_context` for that account. Follow its voice, audience, guardrails and facts over the skill's writing defaults.
4. For a recurring series, use `next_in_series` for its format, previous installment and next number.
5. Use `set_context` only when the user wants a durable preference saved; a tone correction for this draft is not automatically a request to persist it.

A request for copy can be answered in the conversation without `create_post`. Save a draft when the user asks to save, post or schedule it. If no account or connector is available, still draft the text and explain what is needed to schedule.

## Match the actual publishing path

The implementation reviewed on 2026-10-31 supports LinkedIn member-profile posts with a body and images:

- **Text:** a 3,000-character body limit. postmoderno currently checks Unicode code points, including full URL text, spaces and line breaks. Do not apply X's URL or emoji weighting, or call this proof that every native LinkedIn Unicode edge case is accepted.
- **Images:** up to nine, with alt text. This is the product's declared limit, not a universal statement about LinkedIn's native maximum. Use public image URLs in `media`, or `create_upload_url` for local files.
- **Unsupported here:** video uploads, PDF/document posts, polls and self-reply chains. Do not call `add_reply` for LinkedIn, promise an automatic first-comment link, or treat an image gallery as a PDF document post.
- **Publisher:** the current adapter posts as a connected member. Do not silently substitute a personal profile when the user requested a company Page, or promise Page publishing this adapter does not implement.

Use live tool descriptions and reported capabilities if the connection has changed. A supported capability must actually be offered; a different platform's tool or native LinkedIn feature is not evidence.

For unsupported formats, offer copy for native publishing or a supported alternative that preserves the idea. Get the user's choice before changing their requested format, media or publisher. Do not create a chain of independent posts as a substitute for a reply thread without being asked.

## Save the draft

Use `create_post` with the final body and the selected account in `target_account_ids`. Generate one `idempotency_key` for that exact creation request. After transport uncertainty, reuse it only for an identical retry; never create a fresh key merely because the response was lost.

Prepare and attach the agreed media before previewing. Use `edit_post` to correct a saved draft rather than creating duplicates. Resolve factual placeholders before moving to scheduling.

When adapting one idea for X and LinkedIn, make a platform-appropriate version for each. A shared text body and shared targets are not a substitute for checking both limits and the user's intended wording.

## Preview, confirm, schedule

1. Call `preview_schedule` with the exact saved post and proposed time. For immediate publishing, use `at: "now"`. Do not supply a LinkedIn reply chain.
2. Show the returned local and UTC time, target account, chain size, delivery cost or allowance projection, blockers and warnings. If there are no blockers, say so.
3. Wait for the user's explicit confirmation of that preview. A request to post or a previous draft approval does not replace this confirmation.
4. Call `schedule_post` with the same post, time and returned `preview_revision`.
5. If content, targets, media or time changes, or the revision is rejected, preview again and obtain confirmation of the changed state.

Treat the preview's actual projection as authoritative. Do not apply X's link-cost multiplier to LinkedIn or invent a LinkedIn charge.

## Errors and uncertain outcomes

Read structured errors: explain `message`, follow `next_action` and `next_tool`, respect `acted_by`, and retry a reported error only when `retryable` is true. Preserve creation keys on identical retries.

If a scheduling response is lost, inspect `get_post` before assuming failure or trying a new action. Use returned status to distinguish saved, scheduled and published; never claim that a preview posted anything. Use `diagnose` for an unclear delivery result or relevant briefing warning.

If a required tool is missing, explain the missing permission or connection and continue with the drafting work that is possible. Do not claim to have called a tool that is unavailable.
