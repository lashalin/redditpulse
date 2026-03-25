from __future__ import annotations

SYSTEM_PROMPT = """You are an expert in natural language processing and market research,
specializing in extracting discussion themes from social media data.

Your job is to identify the key topics being discussed about a brand on Reddit,
cluster them into meaningful categories, and assess the volume and sentiment of each.

Rules:
- Use the predefined category framework as a starting point, but add new categories if the data demands it
- Each topic must be supported by actual post examples from the data
- Quantify everything: how many posts mention this topic, what's the average sentiment
- Output language: Match the user's language context
"""

USER_PROMPT_TEMPLATE = """Analyze discussions about "{brand}" and cluster them into topics.

## Post Titles and Bodies:
{posts_data}

## Predefined Category Framework (adapt as needed):
1. Product Features & Quality
2. Pricing & Value for Money
3. Competitor Comparisons
4. Customer Service & Support
5. Use Cases & Tutorials
6. Purchase & Availability
7. Bugs & Technical Issues
8. Brand Reputation & Trust
9. Industry News & Updates
10. Memes & Community Culture

## Required Output:

### Topic Clusters (ranked by post volume)

For each topic:
**Topic Name**: [descriptive name]
- **Category**: [from framework above, or new]
- **Post Count**: [estimated count from the data]
- **Sentiment**: [positive/negative/neutral + score]
- **Key Phrases**: [3-5 recurring phrases/keywords]
- **Representative Posts**: [2-3 post titles that best represent this topic]
- **Trend**: [growing/stable/declining based on date distribution]
- **Brand Implication**: [what this means for the brand in 1 sentence]

### Cross-Topic Insights
- Which topics overlap? (e.g., pricing complaints often appear alongside competitor comparisons)
- Are there seasonal or event-driven spikes?
- What's the ratio of product-related vs brand-related discussions?

### Underserved Topics
- Topics with high engagement but few quality responses
- Questions that keep recurring without satisfactory answers
"""


def build_prompt(brand: str, posts: list[dict]) -> tuple[str, str]:
    """Build the topic clustering prompt."""
    posts_text = ""
    for i, post in enumerate(posts[:50], 1):
        body_preview = (post.get("body", "") or "")[:200]
        posts_text += (
            f"{i}. [{post.get('subreddit', '?')}] "
            f"(score:{post.get('score', 0)}, sentiment:{post.get('sentiment_label', '?')}) "
            f"{post.get('title', 'N/A')}"
        )
        if body_preview:
            posts_text += f"\n   Body: {body_preview}"
        posts_text += "\n"

    user_prompt = USER_PROMPT_TEMPLATE.format(
        brand=brand,
        posts_data=posts_text,
    )
    return SYSTEM_PROMPT, user_prompt
