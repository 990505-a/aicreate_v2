"""Unit tests for RSSHub client."""

import pytest
from unittest.mock import AsyncMock, patch
from app.tools.rsshub import RSSHubClient


class TestRSSHubClient:
    """Test RSSHub client functionality."""

    @pytest.fixture
    def client(self):
        """Create RSSHub client instance."""
        return RSSHubClient(instance_url="https://test.rsshub.app")

    @pytest.mark.asyncio
    async def test_fetch_feed_success(self, client):
        """Test successful RSS feed fetching."""
        mock_response = """
        <?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <title>Test Feed</title>
                <description>Test Description</description>
                <link>https://test.com</link>
                <language>en</language>
                <item>
                    <title>Test Article</title>
                    <description>Test content</description>
                    <link>https://test.com/article</link>
                    <pubDate>Wed, 14 Jan 2026 12:00:00 GMT</pubDate>
                    <author>Test Author</author>
                </item>
            </channel>
        </rss>
        """

        with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value.raise_for_status = lambda: None
            mock_get.return_value.text = mock_response

            result = await client.fetch_feed("/test/route")

            assert result is not None
            assert result["title"] == "Test Feed"
            assert result["description"] == "Test Description"
            assert len(result["entries"]) == 1
            assert result["entries"][0]["title"] == "Test Article"

    @pytest.mark.asyncio
    async def test_fetch_feed_failure(self, client):
        """Test failed RSS feed fetching."""
        with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
            from httpx import HTTPStatusError

            response_mock = AsyncMock()
            response_mock.raise_for_status.side_effect = HTTPStatusError(
                "404 Not Found", request=None, response=response_mock
            )
            mock_get.return_value = response_mock

            result = await client.fetch_feed("/nonexistent/route")

            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_multiple_feeds(self, client):
        """Test fetching multiple feeds concurrently."""
        routes = [
            {"route": "/route1", "source": "source1", "category": "News"},
            {"route": "/route2", "source": "source2", "category": "Tech"},
        ]

        mock_feed_data = {
            "title": "Feed",
            "description": "Desc",
            "link": "https://test.com",
            "language": "en",
            "entries": [{"title": "Article"}],
        }

        with patch.object(client, "fetch_feed", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_feed_data

            results = await client.fetch_multiple_feeds(routes)

            assert len(results) == 2
            assert all(r is not None for r in results)
            assert results[0]["source"] == "source1"
            assert results[1]["source"] == "source2"

    def test_filter_recent_entries(self, client):
        """Test filtering entries by time."""
        from datetime import datetime, timedelta

        now = datetime.utcnow()
        entries = [
            {"published": (now - timedelta(hours=1)).strftime("%a, %d %b %Y %H:%M:%S %z")},
            {"published": (now - timedelta(hours=25)).strftime("%a, %d %b %Y %H:%M:%S %z")},
            {"published": (now - timedelta(hours=2)).strftime("%a, %d %b %Y %H:%M:%S %z")},
        ]

        filtered = client.filter_recent_entries(entries, hours=24)

        assert len(filtered) == 2
        assert all("published" in e for e in filtered)

    def test_filter_entries_without_date(self, client):
        """Test that entries without dates are included."""
        entries = [
            {"title": "No date", "content": "Content"},
            {
                "title": "Has date",
                "published": "Wed, 14 Jan 2026 12:00:00 GMT",
                "content": "Content",
            },
        ]

        filtered = client.filter_recent_entries(entries, hours=1)

        # Both should be included (no date articles are kept)
        assert len(filtered) == 2

    @pytest.mark.asyncio
    async def test_close_client(self, client):
        """Test closing the HTTP client."""
        with patch.object(client.client, "aclose", new_callable=AsyncMock) as mock_close:
            await client.close()
            mock_close.assert_called_once()
