from __future__ import annotations

SYSTEM_PROMPT = """You are a senior social media analyst specializing in Reddit content analysis.
You have deep expertise in identifying viral patterns, community dynamics, and brand perception on Reddit.

Your analysis must be:
- Data-driven: reference specific post metrics (score, comments, upvote ratio)
- Insight-rich: go beyond surface-level observations
- Actionable: every insight should have a "so what" implication
- Honest: if sentiment is negative, say so clearly

Output language: Match the user's language. If the brand/data is in Chinese context, respond in Chinese.
"""

USER_PROMPT_TEMPLATE = """Analyze the following top Reddit posts about "{brand}" and provide a comprehensive hot posts summary.

## Post Data:
{posts_data}

## Required Output Format:

### 1. Top Posts Overview
For each of the top 10 posts (by score):
- **Title**: [post title]
- **Subreddit**: r/[subreddit] | Score: [score] | Comments: [num]
- **Why it went viral**: [1-2 sentence analysis of what made this post resonate]
- **Key takeaway for brand**: [actionable insight]

### 2. Viral Pattern Analysis
- What content formats perform best? (question, review, comparison, tutorial, meme, news)
- What emotional triggers drive engagement? (frustration, excitement, curiosity, humor)
- What time patterns exist in successful posts?

### 3. Comment Sentiment Deep Dive
For the top 5 most-discussed posts:
- Main arguments FOR the brand
- Main arguments AGAINST the brand
- Surprising/unexpected opinions that appeared frequently

### 4. Content Gap Opportunities
- Topics users are asking about but getting few quality answers
- Complaints that the brand could address with content
- Comparisons where the brand could position itself better

### 5. Risk Alerts
- Any posts showing signs of a PR crisis or viral negativity
- Common misconceptions being spread
- Competitor-favorable narratives gaining traction
"""


def build_prompt(brand: str, posts: list[dict]) -> tuple[str, str]:
    """Build the hot posts summary prompt."""
    posts_text = ""
    for i, post in enumerate(posts[:30], 1):
        posts_text += f"""
Post #{i}:
- Title: {post.get('title', 'N/A')}
- Subreddit: r/{post.get('subreddit', 'N/A')}
- Score: {post.get('score', 0)} | Comments: {post.get('num_comments', 0)} | Upvote Ratio: {post.get('upvote_ratio', 'N/A')}
- Author: {post.get('author', 'N/A')}
- Date: {post.get('created_utc', 'N/A')}
- Body Preview: {(post.get('body', '') or '')[:300]}
- Top Comments: {_format_comments(post.get('top_comments', []))}
---"""

    user_prompt = USER_PROMPT_TEMPLATE.format(
        brand=brand,
        posts_data=posts_text,
    )
    return SYSTEM_PROMPT, user_prompt


def _format_comments(comments: list[dict]) -> str:
    if not comments:
        return "N/A"
    lines = []
    for c in comments[:5]:
        lines.append(f"  [{c.get('score', 0)} pts] {(c.get('body', ''))[:150]}")
    return "\n".join(lines)
