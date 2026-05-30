"""npmjs unit tests."""

import unittest
from datetime import UTC, datetime
from unittest.mock import Mock, patch

from npmjs import get_publication_datetime

from .helpers import mock_response


class NpmjsPublicationDatetimeTest(unittest.TestCase):
    """Unit tests for the npmjs publication datetime fetcher."""

    @patch("requests.get", Mock(return_value=mock_response({"time": {"1.0": "20260530T10:14:40.567Z"}})))
    def test_get_publication_datetime(self):
        """Test that the publication datetime can be fetched."""
        publication_datetime = datetime(2026, 5, 30, 10, 14, 40, 567000, tzinfo=UTC)
        self.assertEqual(publication_datetime, get_publication_datetime("package", "1.0"))
