from __future__ import annotations

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class SentimentAnalyzer:
    """VADER-based sentiment analysis for Reddit posts and comments.

    Free, fast, no API calls needed.
    Specifically tuned for social media text (slang, emojis, etc).
    """

    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze(self, text: str) -> dict:
        """Analyze sentiment of a single text.

        Returns:
            {
                "label": "positive" | "negative" | "neutral",
                "score": float (-1 to 1),
                "details": {"pos": float, "neg": float, "neu": float, "compound": float}
            }
        """
        if not text or not text.strip():
            return {"label": "neutral", "score": 0.0, "details": {}}

        scores = self.analyzer.polarity_scores(text)
        compound = scores["compound"]

        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        return {
            "label": label,
            "score": compound,
            "details": scores,
        }

    def analyze_batch(self, texts: list[str]) -> list[dict]:
        """Analyze sentiment for a batch of texts."""
        return [self.analyze(text) for text in texts]

    def get_distribution(self, results: list[dict]) -> dict:
        """Calculate sentiment distribution from analysis results."""
        total = len(results)
        if total == 0:
            return {"positive": 0, "negative": 0, "neutral": 0, "avg_score": 0}

        positive = sum(1 for r in results if r["label"] == "positive")
        negative = sum(1 for r in results if r["label"] == "negative")
        neutral = sum(1 for r in results if r["label"] == "neutral")
        avg_score = sum(r["score"] for r in results) / total

        return {
            "positive": round(positive / total * 100, 1),
            "negative": round(negative / total * 100, 1),
            "neutral": round(neutral / total * 100, 1),
            "avg_score": round(avg_score, 3),
            "total_analyzed": total,
        }
