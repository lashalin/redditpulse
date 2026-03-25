"""Core analysis engine - orchestrates crawling, sentiment, and LLM analysis."""

from __future__ import annotations

import json
from collections import Counter
from app.services.reddit_crawler import RedditCrawler
from app.services.sentiment import SentimentAnalyzer
from app.services.llm_provider import get_llm_provider
from app.prompts import hot_posts_summary, topic_clustering, subreddit_profile, marketing_advice


class BrandAnalyzer:
    """Full brand analysis pipeline: crawl → filter → sentiment → LLM insights."""

    def __init__(self):
        self.crawler = RedditCrawler()
        self.sentiment = SentimentAnalyzer()
        self.llm = get_llm_provider()

    def _llm_relevance_filter(self, keyword: str, posts: list[dict]) -> list[dict]:
        """Use LLM to filter out posts that are not actually about the brand.

        This catches cases where the keyword matches but the context is wrong,
        e.g., 'anker' in German posts meaning 'anchor', or name coincidences.
        """
        if not posts:
            return posts

        # Build a compact list of titles for the LLM to evaluate
        # Process in batches to stay within token limits
        batch_size = 50
        relevant_ids = set()

        for i in range(0, len(posts), batch_size):
            batch = posts[i:i + batch_size]
            post_list = []
            for idx, p in enumerate(batch):
                post_list.append(f'{idx}. [{p["subreddit"]}] {p["title"][:120]}')

            posts_text = "\n".join(post_list)

            prompt = f"""You are a brand relevance filter. Given the brand/product keyword "{keyword}",
determine which Reddit posts are ACTUALLY about this brand/product/company.

IMPORTANT RULES:
- "{keyword}" is a BRAND/PRODUCT name, not a common word
- Posts must be discussing the actual brand/company/product "{keyword}"
- Filter OUT posts where "{keyword}" appears as a different meaning (e.g., a person's name, a word in another language, or completely unrelated context)
- Filter OUT posts from clearly unrelated subreddits (e.g., comics, memes, politics) unless they specifically discuss the brand
- Keep posts about: product reviews, comparisons, recommendations, customer experiences, deals, technical discussions, brand news

Here are the posts (format: index. [subreddit] title):

{posts_text}

Return ONLY a JSON array of the index numbers of posts that are RELEVANT to the brand "{keyword}".
Example response: [0, 2, 5, 7]

If none are relevant, return: []
Return ONLY the JSON array, nothing else."""

            try:
                response = self.llm.generate(prompt, system_prompt="You are a precise content filter. Return only valid JSON arrays.")
                # Parse the response - extract JSON array
                response = response.strip()
                # Find JSON array in response
                start = response.find('[')
                end = response.rfind(']') + 1
                if start >= 0 and end > start:
                    indices = json.loads(response[start:end])
                    for idx in indices:
                        if isinstance(idx, int) and 0 <= idx < len(batch):
                            relevant_ids.add(batch[idx]["reddit_id"])
                else:
                    # If parsing fails, keep all posts in this batch
                    print(f"LLM filter: Could not parse response, keeping all posts in batch")
                    for p in batch:
                        relevant_ids.add(p["reddit_id"])
            except Exception as e:
                print(f"LLM relevance filter error: {e}, keeping all posts in batch")
                for p in batch:
                    relevant_ids.add(p["reddit_id"])

        filtered = [p for p in posts if p["reddit_id"] in relevant_ids]
        print(f"LLM relevance filter: {len(posts)} → {len(filtered)} posts "
              f"({len(posts) - len(filtered)} removed as irrelevant)")
        return filtered

    def run_full_analysis(self, keyword: str, time_range: str = "3m") -> dict:
        """Run the complete analysis pipeline for a brand keyword."""

        # Step 1: Crawl Reddit posts (limit to 150, will filter down)
        raw_posts = self.crawler.search_posts(keyword, time_range=time_range, limit=150)
        if not raw_posts:
            return {"error": "No posts found for this keyword", "keyword": keyword}

        # Step 2: LLM-based relevance filter (removes off-topic posts)
        posts = self._llm_relevance_filter(keyword, raw_posts)
        if not posts:
            return {"error": "No relevant posts found for this brand", "keyword": keyword}

        # Step 3: Sentiment analysis on all posts
        for post in posts:
            text = f"{post['title']} {post.get('body', '')}"
            result = self.sentiment.analyze(text)
            post["sentiment_label"] = result["label"]
            post["sentiment_score"] = result["score"]

        sentiment_results = [
            {"label": p["sentiment_label"], "score": p["sentiment_score"]}
            for p in posts
        ]
        sentiment_dist = self.sentiment.get_distribution(sentiment_results)

        # Step 4: Fetch comments for top posts
        top_posts = sorted(posts, key=lambda x: x["score"], reverse=True)[:5]
        for post in top_posts:
            comments = self.crawler.get_post_comments(post["reddit_id"], limit=10)
            # Analyze comment sentiment
            for comment in comments:
                c_result = self.sentiment.analyze(comment["body"])
                comment["sentiment_label"] = c_result["label"]
                comment["sentiment_score"] = c_result["score"]
            post["top_comments"] = comments

        # Step 5: Build subreddit profiles
        subreddit_counts = Counter(p["subreddit"] for p in posts)
        subreddit_data = []
        for sub_name, count in subreddit_counts.most_common(8):
            sub_info = self.crawler.get_subreddit_info(sub_name)
            sub_posts = [p for p in posts if p["subreddit"] == sub_name]
            avg_sent = (
                sum(p["sentiment_score"] for p in sub_posts) / len(sub_posts)
                if sub_posts
                else 0
            )
            subreddit_data.append({
                "name": sub_name,
                "subscriber_count": sub_info.get("subscriber_count") if sub_info else None,
                "description": sub_info.get("description", "") if sub_info else "",
                "post_count": count,
                "avg_sentiment": round(avg_sent, 3),
                "sample_titles": [p["title"] for p in sub_posts[:5]],
            })

        # Step 6: LLM Analysis (Gemini)
        # 6a. Hot posts summary
        sys_prompt, user_prompt = hot_posts_summary.build_prompt(keyword, top_posts)
        hot_posts_text = self.llm.generate(user_prompt, system_prompt=sys_prompt)

        # 6b. Topic clustering
        sys_prompt, user_prompt = topic_clustering.build_prompt(keyword, posts)
        topics_text = self.llm.generate(user_prompt, system_prompt=sys_prompt)

        # 6c. Subreddit profiles
        sys_prompt, user_prompt = subreddit_profile.build_prompt(keyword, subreddit_data)
        subreddit_text = self.llm.generate(user_prompt, system_prompt=sys_prompt)

        # 6d. Marketing advice (uses all above as input)
        sentiment_for_advice = {
            "overall_label": self._overall_label(sentiment_dist["avg_score"]),
            "avg_score": sentiment_dist["avg_score"],
            "positive": sentiment_dist["positive"],
            "neutral": sentiment_dist["neutral"],
            "negative": sentiment_dist["negative"],
        }
        sys_prompt, user_prompt = marketing_advice.build_prompt(
            brand=keyword,
            total_posts=len(posts),
            time_range=time_range,
            sentiment_data=sentiment_for_advice,
            subreddit_summary=subreddit_text[:2000],
            topic_summary=topics_text[:2000],
            hot_posts_summary=hot_posts_text[:2000],
        )
        advice_text = self.llm.generate(user_prompt, system_prompt=sys_prompt)

        # Step 7: Compile results
        return {
            "keyword": keyword,
            "time_range": time_range,
            "stats": {
                "total_posts": len(posts),
                "total_subreddits": len(subreddit_counts),
                "sentiment": sentiment_dist,
                "raw_crawled": len(raw_posts),
                "filtered_relevant": len(posts),
            },
            "posts": [self._serialize_post(p) for p in posts],
            "top_posts": [self._serialize_post(p) for p in top_posts],
            "subreddits": subreddit_data,
            "analysis": {
                "hot_posts_summary": hot_posts_text,
                "topic_clusters": topics_text,
                "subreddit_profiles": subreddit_text,
                "marketing_advice": advice_text,
            },
        }

    def _serialize_post(self, post: dict) -> dict:
        """Serialize post for JSON response."""
        serialized = {**post}
        if "created_utc" in serialized:
            serialized["created_utc"] = str(serialized["created_utc"])
        if "top_comments" in serialized:
            for c in serialized["top_comments"]:
                if "created_utc" in c:
                    c["created_utc"] = str(c["created_utc"])
        return serialized

    def _overall_label(self, score: float) -> str:
        if score >= 0.05:
            return "positive"
        elif score <= -0.05:
            return "negative"
        return "neutral"
