"""RSSHub integration tools."""

import asyncio
import httpx
from typing import List, Dict, Optional, AsyncIterator
from datetime import datetime, timedelta
from feedparser import parse
from loguru import logger

from app.core.config import get_settings
from app.monitoring import rsshub_requests_total, rsshub_request_duration_seconds

settings = get_settings()


class RSSHubClient:
    """Client for interacting with RSSHub."""

    def __init__(self, instance_url: Optional[str] = None):
        self.instance_url = instance_url or settings.rsshub_instance
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": "https://rsshub.app/",
            }
        )
        self._last_request_time: Dict[str, datetime] = {}

    async def fetch_feed(
        self, route: str, params: Optional[Dict] = None, use_cache: bool = True
    ) -> Optional[Dict]:
        """Fetch RSS feed from RSSHub."""
        start_time = datetime.utcnow()
        url = f"{self.instance_url}{route}"

        # Rate limiting
        if route in self._last_request_time:
            time_since_last = (datetime.utcnow() - self._last_request_time[route]).total_seconds()
            if time_since_last < settings.rsshub_rate_limit_delay:
                await asyncio.sleep(settings.rsshub_rate_limit_delay - time_since_last)

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()

            # Parse feed
            feed = parse(response.content)

            # Update timing
            duration = (datetime.utcnow() - start_time).total_seconds()
            self._last_request_time[route] = datetime.utcnow()

            # Record metrics
            rsshub_requests_total.labels(route=route, status="success").inc()
            rsshub_request_duration_seconds.labels(route=route).observe(duration)

            # Return structured data
            return {
                "title": feed.feed.get("title", ""),
                "description": feed.feed.get("description", ""),
                "link": feed.feed.get("link", ""),
                "language": feed.feed.get("language", ""),
                "entries": [
                    {
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "description": entry.get("description", entry.get("summary", "")),
                        "published": entry.get("published", ""),
                        "author": entry.get("author", ""),
                        "tags": [tag.term for tag in entry.get("tags", [])],
                        "enclosures": [
                            {
                                "url": enc.get("url", ""),
                                "type": enc.get("type", ""),
                                "length": enc.get("length", 0),
                            }
                            for enc in entry.get("enclosures", [])
                        ],
                    }
                    for entry in feed.entries
                ],
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"RSSHub HTTP error for {url}: {e}")
            rsshub_requests_total.labels(route=route, status="error").inc()
            return None
        except Exception as e:
            logger.error(f"Error fetching RSS feed from {url}: {e}")
            rsshub_requests_total.labels(route=route, status="error").inc()
            return None

    async def fetch_multiple_feeds(self, routes: List[Dict], max_concurrent: int = 5) -> List[Dict]:
        """Fetch multiple RSS feeds concurrently."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_with_semaphore(route_config: Dict):
            async with semaphore:
                route = route_config["route"]
                params = route_config.get("params", {})
                feed = await self.fetch_feed(route, params)

                if feed:
                    return {
                        "source": route_config.get("source", route),
                        "category": route_config.get("category", "General"),
                        "feed": feed,
                    }
                return None

        tasks = [fetch_with_semaphore(route_config) for route_config in routes]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [result for result in results if result and not isinstance(result, Exception)]

    def filter_recent_entries(self, entries: List[Dict], hours: int = 24) -> List[Dict]:
        """Filter entries from the last N hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        filtered = []
        for entry in entries:
            try:
                # Parse publication date
                pub_date_str = entry.get("published", "")
                if pub_date_str:
                    # Try different date formats
                    for date_format in [
                        "%a, %d %b %Y %H:%M:%S %z",
                        "%a, %d %b %Y %H:%M:%S %Z",
                        "%Y-%m-%dT%H:%M:%S%z",
                        "%Y-%m-%d %H:%M:%S",
                    ]:
                        try:
                            pub_date = datetime.strptime(pub_date_str, date_format)
                            # Make timezone-aware if needed
                            if pub_date.tzinfo:
                                pub_date = pub_date.replace(tzinfo=None) - pub_date.utcoffset()

                            if pub_date > cutoff_time:
                                filtered.append(entry)
                            break
                        except ValueError:
                            continue
                else:
                    # No date, include it
                    filtered.append(entry)
            except Exception as e:
                logger.warning(f"Error parsing date for entry: {e}")
                # Include entry if we can't parse the date
                filtered.append(entry)

        return filtered

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global RSSHub client
rsshub_client = RSSHubClient()


async def get_rsshub_client() -> RSSHubClient:
    """Get RSSHub client instance."""
    return rsshub_client
