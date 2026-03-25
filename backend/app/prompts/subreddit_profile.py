from __future__ import annotations

SYSTEM_PROMPT = """You are a Reddit community expert with deep knowledge of subreddit cultures,
moderation styles, and unwritten rules. You've spent years observing how brands succeed
and fail in different Reddit communities.

Your subreddit profiles must help marketers understand:
- Whether a subreddit is safe for brand engagement
- What content styles are welcomed vs. rejected
- The real rules (not just sidebar rules) of the community

Be brutally honest about marketing-hostile subreddits. A wrong recommendation
could get a brand permanently banned.

Output language: Match the user's language context.
"""

USER_PROMPT_TEMPLATE = """Create detailed profiles for subreddits where "{brand}" is being discussed.

## Subreddit Data:
{subreddit_data}

## Required Output for Each Subreddit:

### r/[subreddit_name]
**Basic Stats**:
- Subscribers: [count] | Active Users: [count]
- Brand mentions found: [count] posts
- Average sentiment toward brand: [score]

**Community Character**:
- Vibe: [professional/casual/meme-heavy/toxic/supportive]
- Typical user: [persona description in 1-2 sentences]
- Content style: [long-form discussions/quick questions/news sharing/memes]

**Moderation & Rules**:
- Self-promotion policy: [strict/moderate/lenient]
- Known unwritten rules: [things that get you downvoted even if not against rules]
- Auto-mod behavior: [any known auto-removal patterns]

**Marketing Friendliness Score**: [1-10]
- 1-3: Hostile (will ban brand accounts, downvote anything commercial)
- 4-6: Cautious (organic participation OK, any hint of marketing = destroyed)
- 7-10: Friendly (product discussions welcomed, even direct brand participation)

**Recommended Approach**:
- Content type that works: [specific examples]
- Content type that fails: [specific examples]
- Best posting time (UTC): [estimated]
- Engagement strategy: [how to interact in comments]

**Risk Assessment**:
- Probability of backlash: [low/medium/high]
- Common triggers to avoid: [specific phrases or approaches]

---

### Overall Subreddit Strategy
- **Priority subreddits** (engage first): [list with reasons]
- **Watch-only subreddits** (monitor but don't post): [list with reasons]
- **Avoid subreddits** (too risky): [list with reasons]
"""


def build_prompt(brand: str, subreddits: list[dict]) -> tuple[str, str]:
    """Build the subreddit profile prompt."""
    sub_text = ""
    for sub in subreddits:
        sub_text += f"""
Subreddit: r/{sub.get('name', '?')}
- Subscribers: {sub.get('subscriber_count', 'N/A')}
- Posts about brand: {sub.get('post_count', 0)}
- Average sentiment: {sub.get('avg_sentiment', 'N/A')}
- Description: {sub.get('description', 'N/A')[:300]}
- Sample post titles:
{_format_sample_titles(sub.get('sample_titles', []))}
---"""

    user_prompt = USER_PROMPT_TEMPLATE.format(
        brand=brand,
        subreddit_data=sub_text,
    )
    return SYSTEM_PROMPT, user_prompt


def _format_sample_titles(titles: list[str]) -> str:
    if not titles:
        return "  N/A"
    return "\n".join(f"  · {t}" for t in titles[:5])
