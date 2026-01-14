"""Unit tests for content filter."""

import pytest
from app.utils.content_filter import ContentFilter, FilterResult


class TestContentFilter:
    """Test content filtering functionality."""

    def test_filter_sensitive_keywords(self):
        """Test filtering of sensitive keywords."""
        filter = ContentFilter(strict_mode=False)
        result = filter.filter_text("This is taiwan independence content")

        assert not result.is_safe
        assert "taiwan independence" in result.blocked_keywords
        assert "*" in result.filtered_content

    def test_filter_regex_patterns(self):
        """Test regex pattern filtering."""
        filter = ContentFilter(strict_mode=False)
        result = filter.filter_text("Contact us at +1-555-123-4567")

        assert not result.is_safe
        assert len(result.blocked_patterns) > 0
        assert "[FILTERED]" in result.filtered_content

    def test_safe_content(self):
        """Test that safe content passes through."""
        filter = ContentFilter(strict_mode=False)
        result = filter.filter_text("This is safe content about technology")

        assert result.is_safe
        assert result.filtered_content == "This is safe content about technology"
        assert len(result.blocked_keywords) == 0
        assert len(result.blocked_patterns) == 0

    def test_strict_mode(self):
        """Test strict mode blocks entire content."""
        filter = ContentFilter(strict_mode=True)
        result = filter.filter_text("Some content with t4iw4n in it")

        assert not result.is_safe
        assert result.filtered_content == "[Content filtered due to sensitive keywords]"

    def test_filter_articles(self):
        """Test filtering multiple articles."""
        filter = ContentFilter(strict_mode=False)

        articles = [
            {"title": "Safe Technology News", "description": "Safe content", "content": "Safe"},
            {
                "title": "Sensitive Content",
                "description": "taiwan independence",
                "content": "Sensitive",
            },
            {"title": "Another Safe", "description": "Also safe", "content": "Safe too"},
        ]

        filtered = filter.filter_articles(articles)

        # In non-strict mode, all articles are included but filtered
        assert len(filtered) == 3
        assert filtered[1]["description"] != "taiwan independence"

    def test_add_custom_keyword(self):
        """Test adding custom sensitive keyword."""
        filter = ContentFilter()
        filter.add_keyword("custombadword")

        result = filter.filter_text("This has custombadword in it")

        assert not result.is_safe
        assert "custombadword" in result.blocked_keywords

    def test_add_custom_pattern(self):
        """Test adding custom regex pattern."""
        filter = ContentFilter()
        filter.add_pattern(r"evil\*\*pattern")

        result = filter.filter_text("This has evil**pattern in it")

        assert not result.is_safe
        assert len(result.blocked_patterns) > 0

    def test_empty_text(self):
        """Test filtering empty text."""
        filter = ContentFilter()
        result = filter.filter_text("")

        assert result.is_safe
        assert result.filtered_content == ""

    def test_multiple_sensitive_terms(self):
        """Test filtering content with multiple sensitive terms."""
        filter = ContentFilter(strict_mode=False)
        result = filter.filter_text("Content about t4iw4n and falun gong")

        assert not result.is_safe
        assert len(result.blocked_keywords) >= 2
