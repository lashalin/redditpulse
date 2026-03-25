from __future__ import annotations

SYSTEM_PROMPT = """You are a senior Reddit marketing strategist with 5+ years of hands-on experience
running brand campaigns on Reddit. You've managed accounts for tech brands, DTC brands,
and SaaS companies, and you deeply understand Reddit's anti-marketing culture.

## Your Core Principles:
1. Reddit users DESPISE overt marketing. Being identified as a marketer = instant death
2. The only way to succeed on Reddit is through genuine value: real answers, honest reviews, helpful content
3. Every subreddit is a different country with different customs — one-size-fits-all NEVER works
4. Comment engagement > Post creation. Helpful replies build more trust than self-posts
5. Account history matters — Redditors WILL check your post history
6. Timing matters — posting during peak hours increases visibility, but varies by subreddit
7. Reddit has a long memory — one bad move can follow a brand for years

## What Makes Great Reddit Marketing:
- A brand rep honestly answering tough questions (even negative ones)
- Tutorial/how-to content that solves real problems (not thinly-veiled ads)
- Engaging in existing conversations rather than starting new ones
- Using Reddit's native tone: casual, self-deprecating, honest

## What Gets Brands Destroyed on Reddit:
- Astroturfing (fake user accounts praising the brand)
- "Fellow kids" tone — trying too hard to be hip
- Ignoring criticism or giving corporate PR responses
- Posting the same content across multiple subreddits (crosspost spam)
- Using new accounts with no history to promote products

Output language: Match the user's language context. If the brand targets Chinese market or user speaks Chinese, respond in Chinese.
"""

USER_PROMPT_TEMPLATE = """Based on the following Reddit data analysis for "{brand}", generate a comprehensive Reddit marketing strategy.

## Brand Analysis Summary:
- Total posts found: {total_posts}
- Time range: {time_range}
- Overall sentiment: {overall_sentiment} (score: {sentiment_score})
- Sentiment distribution: Positive {positive_pct}% | Neutral {neutral_pct}% | Negative {negative_pct}%

## Top Subreddits:
{subreddit_summary}

## Top Discussion Topics:
{topic_summary}

## Hot Posts Summary:
{hot_posts_summary}

---

## Generate the Following Marketing Strategy:

### 1. Executive Summary
- Brand's current Reddit presence assessment (1-2 paragraphs)
- Overall opportunity score: [1-10] with justification
- Top 3 immediate opportunities
- Top 3 risks to watch

### 2. Subreddit Entry Strategy (Prioritized)
For each recommended subreddit (top 5):
| Subreddit | Priority | Strategy | Content Angle | Risk Level |
|-----------|----------|----------|---------------|------------|
| r/xxx | High/Med/Low | [approach] | [specific angle] | [risk] |

### 3. Content Strategy
**Content Pillars** (3-5 recurring themes):
For each pillar:
- Theme name
- Why it works on Reddit
- Example post title (ready to use)
- Recommended format (text/image/video/link)
- Target subreddit(s)

**Content Calendar (30-Day Plan)**:
- Week 1 (Days 1-7): Lurk & Learn Phase
  - Join target subreddits, study top posts
  - Start commenting helpfully (no brand mentions)
  - Daily: 3-5 genuine helpful comments

- Week 2 (Days 8-14): Soft Engagement Phase
  - Answer questions related to your product category
  - Share genuinely useful tips (still no direct promotion)
  - Daily: 2-3 helpful comments + 1 value-add reply

- Week 3 (Days 15-21): First Post Phase
  - First organic post (tutorial/guide/comparison)
  - Continue comment engagement
  - Monitor and respond to all replies within 2 hours

- Week 4 (Days 22-30): Scale & Iterate Phase
  - 2-3 posts across different subreddits
  - AMA or Q&A if community is receptive
  - Analyze performance and adjust

### 4. Comment Engagement Playbook
- **How to respond to praise**: [template]
- **How to respond to criticism**: [template]
- **How to respond to competitor comparisons**: [template]
- **How to respond to technical questions**: [template]
- **Phrases to NEVER use**: [list of corporate-speak to avoid]
- **Tone guide**: [specific Reddit-native tone examples]

### 5. Account Strategy
- Use brand account or personal accounts?
- Account naming recommendations
- Profile setup checklist
- Karma building strategy before first brand post

### 6. DO NOT List (Critical)
At least 10 specific things to avoid, each with:
- What NOT to do
- Why it fails on Reddit
- What to do instead

### 7. Competitor Intelligence
Based on the data:
- How are competitors being discussed?
- What are they doing right/wrong on Reddit?
- Opportunities to differentiate

### 8. KPIs & Measurement
- What to track (not just upvotes)
- Realistic benchmarks for month 1/3/6
- Warning signs that strategy needs adjustment
"""


def build_prompt(
    brand: str,
    total_posts: int,
    time_range: str,
    sentiment_data: dict,
    subreddit_summary: str,
    topic_summary: str,
    hot_posts_summary: str,
) -> tuple[str, str]:
    """Build the marketing advice prompt with all analysis data."""
    user_prompt = USER_PROMPT_TEMPLATE.format(
        brand=brand,
        total_posts=total_posts,
        time_range=time_range,
        overall_sentiment=sentiment_data.get("overall_label", "N/A"),
        sentiment_score=sentiment_data.get("avg_score", "N/A"),
        positive_pct=sentiment_data.get("positive", 0),
        neutral_pct=sentiment_data.get("neutral", 0),
        negative_pct=sentiment_data.get("negative", 0),
        subreddit_summary=subreddit_summary,
        topic_summary=topic_summary,
        hot_posts_summary=hot_posts_summary,
    )
    return SYSTEM_PROMPT, user_prompt
