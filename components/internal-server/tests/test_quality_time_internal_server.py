"""Unit tests for the Quality-time internal server."""

import unittest

from fastapi.responses import RedirectResponse

from quality_time_internal_server import redirect_to_docs


class RootRouteTest(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the / route."""

    async def test_redirect(self):
        """Test that / is redirected to /docs."""
        self.assertEqual(RedirectResponse("/docs").headers, redirect_to_docs().headers)
