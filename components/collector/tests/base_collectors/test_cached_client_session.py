"""Unit tests for the client session with cached GET requests."""

import asyncio
from unittest.mock import patch

import aiounittest

from base_collectors.cached_client_session import CachedClientSession


class CachedClientSessionTest(aiounittest.AsyncTestCase):
    """Unit tests for the cached client session class."""

    async def get(self, *args, **kwargs):  # pylint: disable=unused-argument
        """Fake the session.get method."""
        self.get_calls += 1  # pylint: disable=no-member
        await asyncio.sleep(0)

    @patch("aiohttp.ClientSession.get", new=get)
    async def test_get_same_url_once(self):
        """Test that the url is retrieved once."""
        async with CachedClientSession() as session:
            session.get_calls = 0
            await session.get("https://url")
        self.assertEqual(1, session.get_calls)

    @patch("aiohttp.ClientSession.get", new=get)
    async def test_get_same_url_twice(self):
        """Test that the url is retrieved only once."""
        async with CachedClientSession() as session:
            session.get_calls = 0
            await asyncio.gather(session.get("https://url"), session.get("https://url"))
            await asyncio.gather(session.get("https://url"), session.get("https://url"))
        self.assertEqual(1, session.get_calls)
