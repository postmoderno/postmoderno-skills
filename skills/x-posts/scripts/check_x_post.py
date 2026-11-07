#!/usr/bin/env python3
"""Estimate X draft length and flag possible writing and spam risks.

Usage:
  python3 check_x_post.py < drafts.txt
  python3 check_x_post.py drafts.txt [--limit 280] [--json]

Separate the posts of a thread with a line containing only ---.
To check several alternative single posts at once, separate them with a line
containing only === (each block is then checked as its own post or thread).

Length estimates twitter-text v3: code points U+0000-U+10FF and a few
punctuation ranges count 1, everything else 2, each emoji sequence 2, each
URL 23. Bare domains count as URLs when their suffix is a TLD, as X links
them. This is NOT the full twitter-text parser: the suffix list and emoji
recognition are incomplete. Use the official library or X composer for exact
validation, particularly near the limit. Flags are heuristics, not spam verdicts.
"""

import argparse
import json
import re
import sys
import unicodedata

LIMIT = 280
URL_WEIGHT = 23
ONE_WEIGHT_RANGES = ((0x0000, 0x10FF), (0x2000, 0x200D), (0x2010, 0x201F), (0x2032, 0x2037))

GTLDS = {
    "com", "net", "org", "edu", "gov", "mil", "int", "info", "biz", "name", "pro",
    "io", "ai", "dev", "app", "xyz", "news", "blog", "site", "online", "tech",
    "store", "shop", "cloud", "page", "link", "live", "club", "team", "design",
    "studio", "space", "world", "life", "email", "tools", "software", "agency",
    "media", "social", "network", "digital", "global", "today", "games", "art",
}
CCTLDS = set("""
ac ad ae af ag ai al am ao aq ar as at au aw ax az ba bb bd be bf bg bh bi bj bm bn bo br bs bt
bw by bz ca cc cd cf cg ch ci ck cl cm cn co cr cu cv cw cx cy cz de dj dk dm do dz ec ee eg er
es et eu fi fj fk fm fo fr ga gd ge gf gg gh gi gl gm gn gp gq gr gs gt gu gw gy hk hm hn hr ht
hu id ie il im in io iq ir is it je jm jo jp ke kg kh ki km kn kp kr kw ky kz la lb lc li lk lr
ls lt lu lv ly ma mc md me mg mh mk ml mm mn mo mp mq mr ms mt mu mv mw mx my mz na nc ne nf ng
ni nl no np nr nu nz om pa pe pf pg ph pk pl pm pn pr ps pt pw py qa re ro rs ru rw sa sb sc sd
se sg sh si sk sl sm sn so sr ss st su sv sx sy sz tc td tf tg th tj tk tl tm tn to tr tt tv tw
tz ua ug uk us uy uz va vc ve vg vi vn vu wf ws ye yt za zm zw
""".split())

SCHEMED = re.compile(r'https?://[^\s<>"“”]+', re.IGNORECASE)
BARE = re.compile(r"(?<![\w@.\-])((?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+([a-z]{2,24}))(?![a-z0-9-])(?::[0-9]{1,5})?(?:[/?#][^\s<>\"“”]*)?", re.IGNORECASE)
TRAILING = ".,;:!?)]}'\"…"
MENTION = re.compile(r"(?<![\w@])@[A-Za-z0-9_]{1,15}(?![A-Za-z0-9_])")
HASHTAG = re.compile(r"(?<![\w#&])#\w*[^\W\d]\w*")

BAIT = [
    r"\blike (this )?if\b", r"\b(re)?tweet (this )?if\b", r"\brepost (this )?if\b",
    r"\b(rt|repost|retweet) (to|this|for)\b", r"\blike (and|&|\+) (rt|retweet|repost|share)\b",
    r"\bfollow (me|for more|@)", r"\bdrop an? .{1,20} (below|in the (replies|comments))",
    r"\b(comment|reply) (below|with|\")", r"\btag (someone|a friend|a founder|\d+)",
    r"\bsmash (that|the)\b", r"\bbookmark (this|for later)\b", r"\bdon'?t forget to (like|follow|share)\b",
]
FILLER_CLOSERS = [r"\bthoughts\s*\?", r"\bagree\s*\?", r"\bwhat do you think\s*\?", r"👇"]
AI_TELLS = [
    r"\bhere'?s the thing\b", r"\blet'?s dive in\b", r"\bdive (deep )?into\b", r"\bgame[- ]changer\b",
    r"\bunlock(ing)?\b", r"\bin today'?s (fast-paced|digital|ever-changing)\b", r"\bread that again\b",
    r"\bthis is huge\b", r"\bbuckle up\b", r"🧵", r"\ba thread\b", r"\blet that sink in\b",
    r"\bsecret sauce\b", r"\blevel up\b", r"\bsupercharge\b", r"\belevate\b", r"\bharness(ing)? the power\b",
    r"\bseamless(ly)?\b", r"\bdelve\b", r"\brevolutioni[sz]e\b", r"\bthe truth is\b", r"\bplot twist\b",
    r"\b(it'?s|this is|that'?s) not (just )?[^.?!\n]{1,40}[,;:—–-]\s*(it'?s|this is|that'?s|but)\b",
    r"\bnot because\b[^.?!\n]{1,40}\bbut because\b",
]


def tld_ok(tld):
    tld = tld.lower()
    return tld in GTLDS or tld in CCTLDS


def url_end(text, start, end):
    """Keep balanced path parentheses; strip punctuation outside the link."""
    pairs = {")": "(", "]": "[", "}": "{"}
    while end > start and text[end - 1] in TRAILING:
        last = text[end - 1]
        if last in pairs:
            segment = text[start:end]
            if segment.count(last) <= segment.count(pairs[last]):
                break
        end -= 1
    return end


def find_urls(text):
    spans = []
    for m in SCHEMED.finditer(text):
        end = url_end(text, m.start(), m.end())
        spans.append((m.start(), end))
    for m in BARE.finditer(text):
        if any(s <= m.start() < e for s, e in spans):
            continue
        if not tld_ok(m.group(2)):
            continue
        end = url_end(text, m.start(), m.end())
        spans.append((m.start(), end))
    return sorted(spans)


def pictographic(cp):
    return (
        0x1F000 <= cp <= 0x1FAFF or 0x2600 <= cp <= 0x27BF or 0x2300 <= cp <= 0x23FF
        or 0x2B00 <= cp <= 0x2BFF or 0x2190 <= cp <= 0x21FF or 0x25A0 <= cp <= 0x25FF
        or cp in (0x203C, 0x2049, 0x2122, 0x2139, 0x24C2, 0x2934, 0x2935, 0x3030, 0x303D, 0x3297, 0x3299)
    )


def modifier(cp):
    return cp in (0xFE0F, 0xFE0E, 0x20E3) or 0x1F3FB <= cp <= 0x1F3FF or 0xE0020 <= cp <= 0xE007F


def regional(cp):
    return 0x1F1E6 <= cp <= 0x1F1FF


def char_weight(cp):
    return 1 if any(lo <= cp <= hi for lo, hi in ONE_WEIGHT_RANGES) else 2


def weighted_length(text):
    text = unicodedata.normalize("NFC", text)
    urls = dict(find_urls(text))
    n, i, total, emoji = len(text), 0, 0, 0
    while i < n:
        if i in urls:
            total += URL_WEIGHT
            i = urls[i]
            continue
        cp = ord(text[i])
        nxt = ord(text[i + 1]) if i + 1 < n else None
        if text[i] in "0123456789#*" and (
            nxt == 0x20E3 or
            (nxt == 0xFE0F and i + 2 < n and ord(text[i + 2]) == 0x20E3)
        ):
            j = i + (2 if nxt == 0x20E3 else 3)
            total, emoji, i = total + 2, emoji + 1, j
            continue
        if regional(cp) and nxt is not None and regional(nxt):
            total, emoji, i = total + 2, emoji + 1, i + 2
            continue
        if pictographic(cp) or (cp in (0xA9, 0xAE) and nxt == 0xFE0F):
            j = i + 1
            while j < n:
                c = ord(text[j])
                if modifier(c):
                    j += 1
                elif c == 0x200D and j + 1 < n and (pictographic(ord(text[j + 1])) or regional(ord(text[j + 1]))):
                    j += 2
                else:
                    break
            total, emoji, i = total + 2, emoji + 1, j
            continue
        total += char_weight(cp)
        i += 1
    return total, emoji


def hits(patterns, text):
    found = []
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            found.append(m.group(0).strip())
    return found


def words(text):
    return set(re.findall(r"[^\W_]{3,}", text.lower()))


def check_post(text, limit):
    raw_length = len(text)
    text = unicodedata.normalize("NFC", text)
    length, emoji = weighted_length(text)
    urls = [text[s:e] for s, e in find_urls(text)]
    mentions = MENTION.findall(text)
    accounts = {m.lower() for m in mentions}
    tags = HASHTAG.findall(text)
    notes = []
    if length > limit:
        notes.append(f"ERROR over the limit by {length - limit}")
    if urls:
        notes.append("link detected: lower median engagement in the cited study is observational; check the current scheduling cost")
    if len(accounts) >= 2:
        notes.append(f"{len(accounts)} accounts mentioned: 2+ distinct accounts, media tags included, can trigger a spam check in the reviewed code; keep only intended tags")
    if len(tags) >= 2:
        notes.append(f"{len(tags)} hashtags: they carry no ranking weight and stuffing is a spam signal; use 0-1")
    for h in hits(BAIT, text):
        notes.append(f'engagement bait: "{h}" (review context; not a classifier verdict)')
    for h in hits(FILLER_CLOSERS, text):
        notes.append(f'filler closer: "{h}" (ask a specific question or end on the point)')
    for h in hits(AI_TELLS, text):
        notes.append(f'possible AI tell: "{h}"')
    if text.count("—") >= 2:
        notes.append(f"{text.count('—')} em dashes: reads machine-written; use commas, periods or colons")
    if emoji >= 3:
        notes.append(f"{emoji} emoji: decoration reads as generated; keep only ones that carry meaning")
    return {
        "length": length, "raw_length": raw_length, "estimated": True,
        "limit": limit, "ok": length <= limit, "urls": urls,
        "mentions": mentions, "hashtags": tags, "emoji": emoji, "notes": notes,
    }


def check_thread(posts, limit):
    results = [check_post(p, limit) for p in posts]
    thread_notes = []
    if len(posts) > 3:
        thread_notes.append(
            f"{len(posts)} posts: later replies have limited feed discovery in the reviewed defaults. "
            "Put the best material early; exact reach depends on candidate sources and experiments."
        )
    if len(posts) > 1 and re.search(r"(🧵|\bthread\b|👇|\(1/\d+\)|\b1/\d*\s*$)", posts[0], re.IGNORECASE) and results[0]["length"] < 120:
        thread_notes.append("post 1 looks like a teaser for the thread; it must stand alone for non-followers")
    sets = [words(p) for p in posts]
    for a in range(len(posts)):
        for b in range(a + 1, len(posts)):
            if sets[a] and sets[b]:
                jac = len(sets[a] & sets[b]) / len(sets[a] | sets[b])
                if jac >= 0.6:
                    thread_notes.append(f"posts {a + 1} and {b + 1} are near-duplicates ({jac:.0%} shared words)")
    return {"posts": results, "thread_notes": thread_notes}


def split_blocks(raw):
    blocks = [b.strip("\n") for b in re.split(r"(?m)^\s*===\s*$", raw)]
    out = []
    for block in blocks:
        posts = [p.strip() for p in re.split(r"(?m)^\s*---\s*$", block)]
        posts = [p for p in posts if p]
        if posts:
            out.append(posts)
    return out


def render(index, total, result):
    lines = []
    head = f"Option {index}" if total > 1 else "Draft"
    n = len(result["posts"])
    lines.append(f"{head}: {'thread of ' + str(n) + ' posts' if n > 1 else 'single post'} (estimated lengths)")
    for i, r in enumerate(result["posts"], 1):
        mark = "ok" if r["ok"] else "TOO LONG"
        label = f"  post {i}/{n}" if n > 1 else "  post"
        lines.append(f"{label}: {r['length']}/{r['limit']} {mark}")
        for note in r["notes"]:
            lines.append(f"    - {note}")
    for note in result["thread_notes"]:
        lines.append(f"  * {note}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?", help="drafts file (default: stdin)")
    ap.add_argument("--limit", type=int, default=LIMIT, help="weighted length limit per post (default 280)")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    args = ap.parse_args()
    raw = open(args.file, encoding="utf-8").read() if args.file else sys.stdin.read()
    blocks = split_blocks(raw)
    if not blocks:
        sys.exit("no posts found")
    results = [check_thread(posts, args.limit) for posts in blocks]
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print("\n\n".join(render(i, len(results), r) for i, r in enumerate(results, 1)))
    sys.exit(0 if all(p["ok"] for r in results for p in r["posts"]) else 1)


if __name__ == "__main__":
    main()
