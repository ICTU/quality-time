"""Unit tests for the client session with cached GET requests."""

import asyncio
from unittest.mock import AsyncMock, patch

import aiounittest

from base_collectors.cached_client_session import CachedClientSession


class CachedClientSessionTest(aiounittest.AsyncTestCase):
    """Unit tests for the cached client session class."""

    async def mocked_get(self, *args, **kwargs):
        self.mocked_get_calls += 1
        await asyncio.sleep(0)

    @patch("aiohttp.ClientSession.get", new=mocked_get)
    async def test_get_same_url_once(self):
        """Test that the url is retrieved once."""
        async with CachedClientSession() as session:
            session.mocked_get_calls = 0
            await session.get("https://url")
        self.assertEqual(1, session.mocked_get_calls)

    @patch("aiohttp.ClientSession.get", new=mocked_get)
    async def test_get_same_url_twice(self):
        """Test that the url is retrieved only once."""
        async with CachedClientSession() as session:
            session.mocked_get_calls = 0
            await asyncio.gather(session.get("https://url"), session.get("https://url"))
            await asyncio.gather(session.get("https://url"), session.get("https://url"))
        self.assertEqual(1, session.mocked_get_calls)
