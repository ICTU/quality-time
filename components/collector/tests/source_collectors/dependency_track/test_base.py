"""Unit tests for the Dependency-Track base collector."""

import asyncio
from unittest.mock import DEFAULT

from source_collectors.dependency_track.base import DependencyTrackBase

from .base_test import DependencyTrackTestCase


class DependencyTrackPaginationTest(DependencyTrackTestCase):
    """Unit tests for the pagination of the Dependency-Track collectors."""

    METRIC_TYPE = "source_up_to_dateness"

    def setUp(self) -> None:
        """Extend to use a page size of one, so that a few projects are enough to need multiple pages."""
        super().setUp()
        self.default_page_size = DependencyTrackBase.PAGE_SIZE
        self.default_max_concurrent_pages = DependencyTrackBase.MAX_CONCURRENT_PAGES
        DependencyTrackBase.PAGE_SIZE = 1

    def tearDown(self) -> None:
        """Extend to restore the page size and the maximum number of concurrent pages."""
        DependencyTrackBase.PAGE_SIZE = self.default_page_size
        DependencyTrackBase.MAX_CONCURRENT_PAGES = self.default_max_concurrent_pages
        super().tearDown()

    async def requested_page_nrs(self, total_count: str = "") -> list[str]:
        """Collect a measurement and return the page numbers requested, in the order they were requested."""
        _, get, _ = await self.collect_measurement_and_mocks(
            get_request_json_return_value=self.projects(),
            get_request_headers={"X-Total-Count": total_count} if total_count else {},
        )
        return [str(call.args[0]).split("pageNumber=")[1] for call in get.call_args_list]

    async def test_without_total_count_header(self):
        """Test that one page is retrieved if Dependency-Track does not return the total count."""
        self.assertEqual(["1"], await self.requested_page_nrs())

    async def test_single_page(self):
        """Test that one page is retrieved if all items fit on one page."""
        self.assertEqual(["1"], await self.requested_page_nrs("1"))

    async def test_multiple_pages(self):
        """Test that all pages are retrieved, in page order."""
        self.assertEqual(["1", "2", "3"], await self.requested_page_nrs("3"))

    async def test_partial_last_page(self):
        """Test that the last page is retrieved even if it is not full."""
        DependencyTrackBase.PAGE_SIZE = 2
        self.assertEqual(["1", "2", "3"], await self.requested_page_nrs("5"))

    async def max_concurrent_pages(self, total_count: str) -> int:
        """Collect a measurement and return the maximum number of pages that were retrieved at the same time."""
        concurrent_pages = max_concurrent_pages = 0

        async def get_page(*args, **kwargs) -> object:  # noqa: ARG001
            """Count how many pages are being retrieved at the same time."""
            nonlocal concurrent_pages, max_concurrent_pages
            concurrent_pages += 1
            max_concurrent_pages = max(max_concurrent_pages, concurrent_pages)
            await asyncio.sleep(0)  # Yield control so that other pages can be retrieved concurrently
            concurrent_pages -= 1
            return DEFAULT  # Have the mock return its return value, that is, the mocked response

        await self.collect_measurement(
            get_request_json_return_value=self.projects(),
            get_request_headers={"X-Total-Count": total_count},
            get_request_side_effect=get_page,
        )
        return max_concurrent_pages

    async def test_pages_are_retrieved_concurrently(self):
        """Test that the pages after the first one are not retrieved one by one."""
        self.assertEqual(4, await self.max_concurrent_pages("5"))  # The four pages after the first one

    async def test_concurrency_is_limited(self):
        """Test that not more pages than the maximum are retrieved at the same time."""
        DependencyTrackBase.MAX_CONCURRENT_PAGES = 2
        self.assertEqual(2, await self.max_concurrent_pages("9"))
