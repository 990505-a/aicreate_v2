"""Content filtering system for China compliance."""

import re
from typing import List, Dict, Set
from dataclasses import dataclass
from loguru import logger

from app.monitoring import content_filter_total


@dataclass
class FilterResult:
    """Result of content filtering."""

    is_safe: bool
    filtered_content: str
    blocked_keywords: List[str]
    blocked_patterns: List[str]


class ContentFilter:
    """Multi-layer content filtering system."""

    # Sensitive keywords for China compliance
    SENSITIVE_KEYWORDS: Set[str] = {
        # Political sensitive terms
        "taiwan independence",
        "taiwan is a country",
        "t4iw4n",
        "tibet independence",
        "xinjiang independence",
        "falun gong",
        "falundafa",
        "tiananmen massacre",
        "june 4th incident",
        "6/4",
        # Violence and extremism
        "terrorist attack",
        "bomb",
        "explosion instructions",
        "how to make a bomb",
        "explosive recipe",
        # Adult content
        "pornography",
        "adult video",
        "xxx",
        "sex video",
        # Gambling
        "online casino",
        "gambling",
        "betting tips",
        # Drugs
        "drug recipe",
        "how to make drugs",
        "methamphetamine recipe",
        # Fraud and scams
        "pyramid scheme",
        "mlm scam",
        "investment fraud",
    }

    # Regex patterns for more sophisticated filtering
    SENSITIVE_PATTERNS: List[re.Pattern] = [
        # Taiwan-related variations
        re.compile(r"t[i1]w[a@]n\s+(?:is\s+(?:a\s+)?country|independ)", re.IGNORECASE),
        # Phone number patterns (for spam)
        re.compile(r"\+?\d{1,3}?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"),
        # Email patterns (for spam)
        re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
        # URL patterns with suspicious domains
        re.compile(
            r"(?:http[s]?://)?(?:www\.)?(?:casino|gambling|porn|xxx|adult)\.[a-zA-Z]{2,}",
            re.IGNORECASE,
        ),
    ]

    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode

    def filter_text(self, text: str) -> FilterResult:
        """Filter text content."""
        if not text:
            return FilterResult(
                is_safe=True, filtered_content="", blocked_keywords=[], blocked_patterns=[]
            )

        blocked_keywords = []
        blocked_patterns = []
        filtered_text = text

        # Keyword filtering
        for keyword in self.SENSITIVE_KEYWORDS:
            if keyword.lower() in text.lower():
                blocked_keywords.append(keyword)
                content_filter_total.labels(filter_type="keyword", result="blocked").inc()

                if self.strict_mode:
                    # Replace entire content
                    filtered_text = "[Content filtered due to sensitive keywords]"
                else:
                    # Replace only the keyword
                    filtered_text = re.sub(
                        re.escape(keyword), "*" * len(keyword), filtered_text, flags=re.IGNORECASE
                    )

        # Pattern filtering
        for pattern in self.SENSITIVE_PATTERNS:
            matches = pattern.findall(filtered_text)
            if matches:
                blocked_patterns.append(pattern.pattern)

                content_filter_total.labels(filter_type="pattern", result="blocked").inc()

                if self.strict_mode:
                    filtered_text = "[Content filtered due to sensitive patterns]"
                else:
                    # Replace matched patterns
                    filtered_text = pattern.sub("[FILTERED]", filtered_text)

        # Record safe filters
        if not blocked_keywords and not blocked_patterns:
            content_filter_total.labels(filter_type="text", result="safe").inc()

        is_safe = not (blocked_keywords or blocked_patterns) or not self.strict_mode

        return FilterResult(
            is_safe=is_safe,
            filtered_content=filtered_text,
            blocked_keywords=blocked_keywords,
            blocked_patterns=blocked_patterns,
        )

    def filter_articles(self, articles: List[Dict]) -> List[Dict]:
        """Filter a list of articles."""
        filtered_articles = []

        for article in articles:
            # Filter title
            title_result = self.filter_text(article.get("title", ""))
            article["title"] = title_result.filtered_content

            # Filter description/summary
            summary_result = self.filter_text(
                article.get("description", article.get("summary", ""))
            )
            article["description"] = summary_result.filtered_content
            article["summary"] = summary_result.filtered_content

            # Filter content
            content_result = self.filter_text(article.get("content", ""))
            article["content"] = content_result.filtered_content

            # Only include article if it's safe or in non-strict mode
            if title_result.is_safe and summary_result.is_safe and content_result.is_safe:
                filtered_articles.append(article)
            elif not self.strict_mode:
                # Include but with filtered content
                filtered_articles.append(article)

        return filtered_articles

    def add_keyword(self, keyword: str):
        """Add a sensitive keyword."""
        self.SENSITIVE_KEYWORDS.add(keyword.lower())
        logger.info(f"Added sensitive keyword: {keyword}")

    def add_pattern(self, pattern: str):
        """Add a sensitive regex pattern."""
        try:
            compiled = re.compile(pattern, re.IGNORECASE)
            self.SENSITIVE_PATTERNS.append(compiled)
            logger.info(f"Added sensitive pattern: {pattern}")
        except re.error as e:
            logger.error(f"Invalid regex pattern: {pattern}, error: {e}")
