"""Unit tests for the issue tracker collectors."""

import unittest
from unittest.mock import MagicMock, patch

from requests.auth import HTTPBasicAuth
from issue_tracker_collectors.base_tracker_collector import BaseTrackerCollector
from model.tracker_issue_status import TrackerIssueStatus


class BaseIssueTrackerTest(unittest.TestCase):
    """Unit tests for the copy source action."""

    def test_get_subclass(self):
        """Test that subclass is returned or not."""

        class Subclass(BaseTrackerCollector):  # skipcq: PYL-W0223
            """Dummy subclass."""

        subclass = BaseTrackerCollector.get_subclass("subclass")
        self.assertEqual(subclass, Subclass)

        no_subclass = BaseTrackerCollector.get_subclass("this does not exist")
        self.assertIs(no_subclass, None)

    @patch.object(
        BaseTrackerCollector,
        "_BaseTrackerCollector__safely_parse_source_response",
        MagicMock(return_value=TrackerIssueStatus(name="test")),
    )
    @patch.object(
        BaseTrackerCollector, "_BaseTrackerCollector__safely_parse_landing_url", MagicMock(return_value="landing_url")
    )
    def test_collect(self):
        """Test the collect method."""
        base_collector = BaseTrackerCollector(tracker={}, tracker_issue="")

        with patch.object(
            BaseTrackerCollector,
            "_BaseTrackerCollector__safely_get_source_response",
            MagicMock(return_value={"response": "test_response", "error": None}),
        ):
            status_dict = base_collector.collect()
            self.assertDictEqual(
                status_dict, {"name": "test", "description": None, "landing_url": "landing_url", "error_message": None}
            )

        with patch.object(
            BaseTrackerCollector,
            "_BaseTrackerCollector__safely_get_source_response",
            MagicMock(return_value={"response": None, "error": "test_error"}),
        ):
            status_dict = base_collector.collect()
            self.assertDictEqual(
                status_dict,
                {"name": "Connection error", "description": None, "landing_url": None, "error_message": "test_error"},
            )

    def test_api_url(self):
        """Test api url."""
        base_collector = BaseTrackerCollector(tracker={"url": "test"}, tracker_issue="")
        self.assertEqual(base_collector._api_url(), "test")  # pylint: disable=protected-access

    def test__safely_get_source_response(self):
        """Test safely parsing source response."""
        base_collector = BaseTrackerCollector(tracker={"url": "test"}, tracker_issue="")

        with patch.object(BaseTrackerCollector, "_get_source_response", MagicMock(return_value="response")):
            response = (
                base_collector._BaseTrackerCollector__safely_get_source_response()  # pylint: disable=protected-access
            )
            self.assertDictEqual(response, {"error": None, "response": "response"})

        with patch.object(BaseTrackerCollector, "_get_source_response", MagicMock(side_effect=RuntimeError)):
            response = (
                base_collector._BaseTrackerCollector__safely_get_source_response()  # pylint: disable=protected-access
            )
            self.assertIs(response["response"], None)
            self.assertTrue(response["error"].startswith("Traceback"))

    @patch("requests.get")
    def test_get_source_response(self, mocked_get):
        """Test getting the source response."""
        base_collector = BaseTrackerCollector(
            tracker={"url": "test", "username": "jadoe", "password": None}, tracker_issue=""
        )
        base_collector._get_source_response("test")  # pylint: disable=protected-access
        mocked_get.assert_called_with("test", auth=None)

        base_collector = BaseTrackerCollector(
            tracker={"url": "test", "username": "jadoe", "password": "secret"}, tracker_issue=""
        )
        base_collector._get_source_response("test")  # pylint: disable=protected-access
        self.assertTrue(mocked_get.call_args_list[1][0], "test")
        self.assertTrue(isinstance(mocked_get.call_args_list[1][1]["auth"], HTTPBasicAuth))

    def test__safely_parse_source_response_500(self):
        """Test parsing the source response."""
        response = MagicMock()
        response.status_code = 500
        response.json = MagicMock()
        response.json.return_value = MagicMock()
        response.json.return_value.get.return_value = "The server crashed."

        base_collector = BaseTrackerCollector(tracker={}, tracker_issue="")
        tracker_status = (
            base_collector._BaseTrackerCollector__safely_parse_source_response(  # pylint: disable=protected-access
                response
            )
        )
        self.assertEqual(tracker_status.name, "Connection error")
        self.assertEqual(tracker_status.error_message, "500: The server crashed.")
        self.assertEqual(tracker_status.description, None)

    def test__safely_parse_source_response_200(self):
        """Test parsing the source response."""
        response = MagicMock()
        response.status_code = 200
        response.json = MagicMock()
        response.json.return_value = MagicMock()
        response.json.return_value.get.return_value = "A successfull result."

        base_collector = BaseTrackerCollector(tracker={}, tracker_issue="")
        tracker_status = (
            base_collector._BaseTrackerCollector__safely_parse_source_response(  # pylint: disable=protected-access
                response
            )
        )
        self.assertEqual(tracker_status.name, "Parse error")
        self.assertIn("NotImplementedError", tracker_status.error_message)
        self.assertEqual(tracker_status.description, None)

    def test__safely_parse_source_response_404(self):
        """Test parsing the source response."""
        response = MagicMock()
        response.status_code = 404
        response.json = MagicMock(side_effect=RuntimeError)

        base_collector = BaseTrackerCollector(tracker={}, tracker_issue="")
        tracker_status = (
            base_collector._BaseTrackerCollector__safely_parse_source_response(  # pylint: disable=protected-access
                response
            )
        )
        self.assertEqual(tracker_status.name, "Connection error")
        self.assertEqual(tracker_status.error_message, "404")
        self.assertEqual(tracker_status.description, None)

    def test__safely_parse_landing_url(self):
        """Test parsing the source response."""
        response = MagicMock()
        response.status_code = 404
        response.json = MagicMock(side_effect=RuntimeError)

        base_collector = BaseTrackerCollector(tracker={}, tracker_issue="")
        landing_url = (
            base_collector._BaseTrackerCollector__safely_parse_landing_url()  # pylint: disable=protected-access
        )
        self.assertEqual(landing_url, "")
