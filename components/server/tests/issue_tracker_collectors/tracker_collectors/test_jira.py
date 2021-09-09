"""Testing the Jira issue tracker."""

import unittest
from unittest.mock import MagicMock

from issue_tracker_collectors.tracker_collectors.jira import Jira


class TestJira(unittest.TestCase):
    """Testing the Jira issue tracker."""

    def test_api_url(self):
        """Test that the correct api url is returned."""
        collector = Jira(tracker={"url": "https://test"}, tracker_issue="iddue_id")
        api_url = collector._api_url()  # pylint: disable=protected-access
        self.assertEqual(api_url, "https://test/rest/api/2/issue/iddue_id?fields=status")

    def test_landing_url(self):
        """Test that the correct human readable landing url is returned."""
        collector = Jira(tracker={"url": "https://test"}, tracker_issue="iddue_id")
        api_url = collector._landing_url()  # pylint: disable=protected-access
        self.assertEqual(api_url, "https://test/browse/iddue_id")

    def test__parse_response(self):
        """Test parsing the source response."""
        response = MagicMock()
        response.status_code = 200
        response.json = MagicMock()
        response.json.return_value = {"fields": {"status": {"name": "test", "description": "this is a test."}}}

        collector = Jira(tracker={}, tracker_issue="")
        tracker_status = collector._parse_source_response(response)  # pylint: disable=protected-access
        self.assertEqual(tracker_status.name, "test")
        self.assertEqual(tracker_status.description, "this is a test.")
