"""Cached client session."""

import asyncio
from typing import Any, cast

import aiohttp
from aiohttp.client import _RequestContextManager
from aiohttp.typedefs import StrOrURL


class CachedClientSession(aiohttp.ClientSession):
    """Cached version of client session."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We don't need a fancy cache with time-to-live or a max size because a new session is created every time the
        # collector wakes up (once every minute by default).
        self.__cache = dict()

    async def get(  # type: ignore
            self, url: StrOrURL, *, allow_redirects: bool = True, **kwargs: Any) -> '_RequestContextManager':
        """Retrieve the url, using a cache."""
        if url in self.__cache:
            if isinstance(self.__cache[url], asyncio.Event):
                await self.__cache[url].wait()  # URL is being retrieved, wait for it
        else:
            event = self.__cache[url] = asyncio.Event()  # Make other callers wait until the URL is retrieved
            self.__cache[url] = await super().get(url, allow_redirects=allow_redirects, **kwargs)
            event.set()  # Signal other callers the URL has been retrieved
        return cast(_RequestContextManager, self.__cache[url])
