from __future__ import annotations

import re
import httpx
import time
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.config import get_settings

settings = get_settings()

# Reddit public JSON API — no API key needed
BASE_URL = "https://www.reddit.com"
HEADERS = {
    "User-Agent": "RedditMarketingTool/1.0 (brand analysis bot)"
}


class RedditCrawler:
    """Crawls Reddit using public JSON endpoints (no API key required)."""

    def __init__(self):
        self._last_request_time = 0
        self._min_interval = 2  # seconds between requests to avoid rate limiting

    def _rate_limit(self):
        """Ensure minimum interval between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_time = time.time()

    def _make_request(self, url: str, params: dict = None) -> Optional[dict]:
        """Make a rate-limited GET request to Reddit's JSON API."""
        self._rate_limit()
        try:
            with httpx.Client(headers=HEADERS, timeout=30, follow_redirects=True) as client:
                response = client.get(url, params=params)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # Rate limited — wait and retry once
                    print("Rate limited by Reddit, waiting 10s...")
                    time.sleep(10)
                    response = client.get(url, params=params)
                    if response.status_code == 200:
                        return response.json()
                print(f"Reddit API error: {response.status_code}")
                return None
        except Exception as e:
            print(f"Request error: {e}")
            return None

    def _check_keyword_relevance(self, keyword: str, title: str, body: str) -> dict:
        """Check if a post is relevant to the brand keyword.

        Returns dict with relevance score and match info.
        """
        kw_lower = keyword.lower()
        title_lower = title.lower()
        body_lower = body.lower()[:2000]  # Only check first 2000 chars of body

        # Build word boundary pattern for the keyword
        # This prevents matching "banker" when searching for "anker"
        kw_pattern = re.compile(r'\b' + re.escape(kw_lower) + r'\b', re.IGNORECASE)

        title_match = bool(kw_pattern.search(title))
        body_match = bool(kw_pattern.search(body_lower))

        score = 0
        if title_match:
            score += 10  # Strong signal: keyword in title
        if body_match:
            score += 5   # Medium signal: keyword in body

        # Check for brand context clues (product, company, brand mentions)
        context_words = [
            "brand", "product", "review", "recommend", "bought", "purchase",
            "quality", "warranty", "customer", "support", "charger", "cable",
            "device", "accessory", "price", "deal", "sale", "discount",
            "alternative", "competitor", "vs", "versus", "compared",
            "experience", "opinion", "thoughts", "worth",
        ]
        full_text = f"{title_lower} {body_lower}"
        context_hits = sum(1 for w in context_words if w in full_text)
        if context_hits >= 2:
            score += 3  # Some commercial/brand context

        return {
            "score": score,
            "title_match": title_match,
            "body_match": body_match,
            "has_context": context_hits >= 2,
        }

    def search_posts(
        self,
        keyword: str,
        time_range: str = "3m",
        limit: int = 500,
    ) -> list[dict]:
        """Search Reddit for posts matching the keyword with relevance filtering."""
        time_filter = self._get_time_filter(time_range)
        cutoff_date = self._get_cutoff_date(time_range)

        all_raw_posts = []

        # Strategy: Multiple search passes for better coverage
        search_queries = [
            f'"{keyword}"',           # Exact phrase match (most precise)
            f'title:"{keyword}"',     # Must be in title
        ]

        for query in search_queries:
            after = None
            fetched = 0
            seen_ids = {p["reddit_id"] for p in all_raw_posts}
            max_per_query = min(limit, 100)  # Cap per query

            while fetched < max_per_query:
                params = {
                    "q": query,
                    "sort": "relevance",
                    "t": time_filter,
                    "limit": min(100, max_per_query - fetched),
                    "type": "link",
                    "restrict_sr": "",
                }
                if after:
                    params["after"] = after

                data = self._make_request(f"{BASE_URL}/search.json", params)
                if not data or "data" not in data:
                    break

                children = data["data"].get("children", [])
                if not children:
                    break

                for item in children:
                    post_data = item.get("data", {})
                    post_id = post_data.get("id", "")

                    # Skip duplicates
                    if post_id in seen_ids:
                        continue
                    seen_ids.add(post_id)

                    post_date = datetime.fromtimestamp(
                        post_data.get("created_utc", 0), tz=timezone.utc
                    )

                    # Skip posts outside our time range
                    if cutoff_date and post_date < cutoff_date:
                        continue

                    title = post_data.get("title", "")
                    body = post_data.get("selftext", "") or ""

                    # ===== RELEVANCE FILTER =====
                    relevance = self._check_keyword_relevance(keyword, title, body)

                    # Must have keyword in title or body (word boundary match)
                    if relevance["score"] < 5:
                        continue

                    all_raw_posts.append({
                        "reddit_id": post_id,
                        "subreddit": post_data.get("subreddit", ""),
                        "title": title,
                        "body": body,
                        "author": post_data.get("author", "[deleted]"),
                        "url": f"https://reddit.com{post_data.get('permalink', '')}",
                        "score": post_data.get("score", 0),
                        "upvote_ratio": post_data.get("upvote_ratio", 0),
                        "num_comments": post_data.get("num_comments", 0),
                        "created_utc": post_date,
                        "_relevance_score": relevance["score"],
                        "_title_match": relevance["title_match"],
                    })

                after = data["data"].get("after")
                fetched += len(children)

                if not after:
                    break

        # Sort by relevance score (title matches first), then by Reddit score
        all_raw_posts.sort(
            key=lambda x: (x["_relevance_score"], x["score"]),
            reverse=True
        )

        # Take top results up to limit
        posts = all_raw_posts[:limit]

        # Clean up internal fields
        for p in posts:
            p.pop("_relevance_score", None)
            p.pop("_title_match", None)

        print(f"Crawled {len(posts)} relevant posts for keyword: {keyword} "
              f"(filtered from {len(all_raw_posts)} raw results)")
        return posts

    def get_post_comments(
        self,
        reddit_id: str,
        limit: int = 50,
    ) -> list[dict]:
        """Fetch top comments for a specific post."""
        comments = []

        data = self._make_request(
            f"{BASE_URL}/comments/{reddit_id}.json",
            params={"sort": "best", "limit": limit}
        )

        if not data or not isinstance(data, list) or len(data) < 2:
            return comments

        # data[1] contains comments
        comment_listing = data[1].get("data", {}).get("children", [])

        for item in comment_listing:
            if item.get("kind") != "t1":
                continue
            comment_data = item.get("data", {})
            body = comment_data.get("body", "")
            if not body or body == "[deleted]" or body == "[removed]":
                continue

            comments.append({
                "reddit_id": comment_data.get("id", ""),
                "body": body,
                "author": comment_data.get("author", "[deleted]"),
                "score": comment_data.get("score", 0),
                "created_utc": datetime.fromtimestamp(
                    comment_data.get("created_utc", 0), tz=timezone.utc
                ),
            })

        print(f"Fetched {len(comments)} comments for post: {reddit_id}")
        return comments

    def get_subreddit_info(self, subreddit_name: str) -> Optional[dict]:
        """Get metadata about a subreddit."""
        data = self._make_request(f"{BASE_URL}/r/{subreddit_name}/about.json")

        if not data or "data" not in data:
            return None

        sub = data["data"]
        return {
            "name": sub.get("display_name", subreddit_name),
            "title": sub.get("title", ""),
            "description": (sub.get("public_description", "") or "")[:500],
            "subscriber_count": sub.get("subscribers", 0),
            "active_users": sub.get("accounts_active", 0) or 0,
            "created_utc": datetime.fromtimestamp(
                sub.get("created_utc", 0), tz=timezone.utc
            ),
        }

    def _get_time_filter(self, time_range: str) -> str:
        """Map time range to Reddit's time filter parameter."""
        mapping = {
            "1m": "month",
            "3m": "year",   # Reddit only supports: hour/day/week/month/year/all
            "6m": "year",   # We filter by cutoff_date for finer control
            "1y": "year",
            "all": "all",
        }
        return mapping.get(time_range, "year")

    def _get_cutoff_date(self, time_range: str) -> Optional[datetime]:
        """Calculate the cutoff date for filtering posts."""
        now = datetime.now(timezone.utc)
        mapping = {
            "1m": timedelta(days=30),
            "3m": timedelta(days=90),
            "6m": timedelta(days=180),
            "1y": timedelta(days=365),
            "all": None,
        }
        delta = mapping.get(time_range)
        return (now - delta) if delta else None
