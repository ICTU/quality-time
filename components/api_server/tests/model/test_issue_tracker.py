"""Unit tests for the issue tracker model class."""

import unittest
from unittest.mock import Mock, patch

import requests

from model.issue_tracker import IssueParameters, IssueSuggestion, IssueTracker, IssueTrackerCredentials
from utils.type import URL

from shared_test_code import disable_logging


class IssueTrackerTest(unittest.TestCase):
    """Unit tests for the issue tracker."""

    ISSUE_TRACKER_URL = URL("https://tracker")
    PROJECT_KEY = "KEY"
    ISSUE_TYPE = "BUG"
    ISSUE_TYPE_ID = "10001"
    ISSUE_SUMMARY = "Issue summary"

    def issue_tracker(
        self,
        *,
        url: URL | None = None,
        api_version: str = "2",
        credentials: IssueTrackerCredentials | None = None,
        issue_labels: list[str] | None = None,
        epic_link: str = "",
    ) -> IssueTracker:
        """Create an issue tracker."""
        issue_parameters = IssueParameters(self.PROJECT_KEY, self.ISSUE_TYPE, issue_labels, epic_link)
        url = self.ISSUE_TRACKER_URL if url is None else url
        if credentials:
            return IssueTracker(url, api_version, issue_parameters, credentials)
        return IssueTracker(url, api_version, issue_parameters)

    def jira_responses(self, api_version: str = "2") -> list[Mock]:
        """Return the Jira responses for the project, issue types, and fields endpoints."""
        project_response = Mock()
        project_response.json.return_value = [{"key": self.PROJECT_KEY, "name": "Project"}]
        issue_types_response = Mock()
        issue_types = [
            {"id": self.ISSUE_TYPE_ID, "name": self.ISSUE_TYPE, "subtask": False},
            {"id": "10002", "name": "Story", "subtask": False},
        ]
        issue_types_response.json.return_value = {"values" if api_version == "2" else "issueTypes": issue_types}
        fields_response = Mock()
        fields_response.json.return_value = {"values" if api_version == "2" else "fields": []}
        return [project_response, issue_types_response, fields_response]

    def test_url(self):
        """Test the issue tracker url."""
        self.assertEqual(self.ISSUE_TRACKER_URL, self.issue_tracker().url)

    def test_username_and_password(self):
        """Test the issue tracker credentials."""
        credentials = IssueTrackerCredentials("username", "password")
        issue_tracker = self.issue_tracker(credentials=credentials)
        self.assertEqual("username", issue_tracker.credentials.username)
        self.assertEqual("password", issue_tracker.credentials.password)

    def test_private_token(self):
        """Test the issue tracker credentials."""
        credentials = IssueTrackerCredentials(private_token="token")  # nosec
        issue_tracker = self.issue_tracker(credentials=credentials)
        self.assertEqual("token", issue_tracker.credentials.private_token)

    def test_issue_labels(self):
        """Test the issue tracker issue labels."""
        issue_tracker = self.issue_tracker(issue_labels=["Label"])
        self.assertEqual(["Label"], issue_tracker.issue_parameters.issue_labels)

    def test_issue_epic_link(self):
        """Test the issue tracker epic link."""
        issue_tracker = self.issue_tracker(epic_link="FOO-42")
        self.assertEqual("FOO-42", issue_tracker.issue_parameters.epic_link)

    @patch("requests.get")
    def test_get_suggestions_with_api_v2(self, requests_get):
        """Test that issue suggestions are returned when the API version is v2."""
        response = Mock()
        response.json.return_value = {"issues": [{"key": "FOO-42", "fields": {"summary": self.ISSUE_SUMMARY}}]}
        requests_get.return_value = response
        expected_suggestions = [IssueSuggestion("FOO-42", "Issue summary")]
        self.assertEqual(expected_suggestions, self.issue_tracker(api_version="2").get_suggestions("Summ"))

    @patch("requests.get")
    def test_get_suggestions_with_api_v3(self, requests_get):
        """Test that issue suggestions are returned when the API version is v3."""
        response = Mock()
        response.json.return_value = {"issues": [{"key": "FOO-42", "fields": {"summary": self.ISSUE_SUMMARY}}]}
        requests_get.return_value = response
        expected_suggestions = [IssueSuggestion("FOO-42", "Issue summary")]
        self.assertEqual(expected_suggestions, self.issue_tracker(api_version="3").get_suggestions("Summ"))

    @disable_logging
    def test_get_suggestions_without_url(self):
        """Test that an empty list of issue suggestions is returned."""
        self.assertEqual([], self.issue_tracker().get_suggestions("Query"))

    @patch("requests.get")
    @patch("requests.post")
    def test_create_issue_with_v2(self, requests_post: Mock, requests_get: Mock):
        """Test that an issue can be created with v2 of the API."""
        requests_get.side_effect = self.jira_responses(api_version="2")
        response = Mock()
        response.json.return_value = {"key": "FOO-42"}
        requests_post.return_value = response
        self.assertEqual(
            ("FOO-42", ""),
            self.issue_tracker(api_version="2").create_issue("Summary", "Description [link|https://example.org]."),
        )
        requests_post.assert_called_with(
            self.ISSUE_TRACKER_URL + "/rest/api/2/issue",
            auth=None,
            headers={},
            json={
                "fields": {
                    "project": {"key": self.PROJECT_KEY},
                    "issuetype": {"id": self.ISSUE_TYPE_ID},
                    "summary": "Summary",
                    "description": "Description [link|https://example.org].",
                }
            },
            timeout=10,
        )

    @patch("requests.get")
    @patch("requests.post")
    def test_create_issue_with_v3(self, requests_post: Mock, requests_get: Mock):
        """Test that an issue can be created with v3 of the API."""
        requests_get.side_effect = self.jira_responses(api_version="3")
        response = Mock()
        response.json.return_value = {"key": "FOO-42"}
        requests_post.return_value = response
        self.assertEqual(
            ("FOO-42", ""),
            self.issue_tracker(api_version="3").create_issue("Summary", "Description [link|https://example.org]."),
        )
        requests_post.assert_called_with(
            self.ISSUE_TRACKER_URL + "/rest/api/3/issue",
            auth=None,
            headers={},
            json={
                "fields": {
                    "project": {"key": self.PROJECT_KEY},
                    "issuetype": {"id": self.ISSUE_TYPE_ID},
                    "summary": "Summary",
                    "description": {
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {"text": "Description ", "marks": [], "type": "text"},
                                    {
                                        "type": "text",
                                        "text": "link",
                                        "marks": [{"attrs": {"href": "https://example.org"}, "type": "link"}],
                                    },
                                    {"text": ".", "marks": [], "type": "text"},
                                ],
                            }
                        ],
                        "type": "doc",
                        "version": 1,
                    },
                }
            },
            timeout=10,
        )

    @patch("requests.get")
    @patch("requests.post")
    def test_create_issue_with_issue_type_id(self, requests_post: Mock, requests_get: Mock):
        """Test that an issue can be created when the issue type id is configured."""
        requests_get.side_effect = self.jira_responses()
        response = Mock()
        response.json.return_value = {"key": "FOO-42"}
        requests_post.return_value = response
        issue_tracker = self.issue_tracker()
        issue_tracker.issue_parameters.issue_type = self.ISSUE_TYPE_ID
        self.assertEqual(("FOO-42", ""), issue_tracker.create_issue("Summary"))
        posted_fields = requests_post.call_args.kwargs["json"]["fields"]
        self.assertEqual({"id": self.ISSUE_TYPE_ID}, posted_fields["issuetype"])

    @patch("requests.get")
    @patch("requests.post")
    def test_create_issue_with_unavailable_issue_type(self, requests_post: Mock, requests_get: Mock):
        """Test that an error message is returned if the issue type is not available, e.g. due to a language change."""
        requests_get.side_effect = self.jira_responses()
        issue_tracker = self.issue_tracker()
        issue_tracker.issue_parameters.issue_type = "TAAK"
        expected_error = (
            "Issue type 'TAAK' is not available in project 'KEY'. Available issue types are: BUG, Story. "
            "Please select an issue type in the issue tracker settings of the report."
        )
        self.assertEqual(("", expected_error), issue_tracker.create_issue("Summary"))
        requests_post.assert_not_called()

    @disable_logging
    @patch("requests.get")
    @patch("requests.post")
    def test_create_issue_when_issue_types_cannot_be_retrieved(self, requests_post: Mock, requests_get: Mock):
        """Test that the configured issue type is passed as name if the issue types cannot be retrieved."""
        requests_get.side_effect = OSError("Something went wrong")
        response = Mock()
        response.json.return_value = {"key": "FOO-42"}
        requests_post.return_value = response
        self.assertEqual(("FOO-42", ""), self.issue_tracker().create_issue("Summary"))
        posted_fields = requests_post.call_args.kwargs["json"]["fields"]
        self.assertEqual({"name": self.ISSUE_TYPE}, posted_fields["issuetype"])

    @disable_logging
    def test_create_issue_with_invalid_url(self):
        """Test that without a valid URL an error message is returned."""
        issue_tracker = self.issue_tracker(url=URL("invalid"))
        self.assertIn(
            issue_tracker.create_issue("New issue"),
            [
                (
                    "",
                    (
                        "Invalid URL 'invalid/rest/api/2/issue': No scheme supplied. Perhaps you meant "
                        "https://invalid/rest/api/2/issue?"
                    ),
                ),
                (
                    "",
                    (
                        "Invalid URL 'invalid/rest/api/2/issue': No scheme supplied. Perhaps you meant "
                        "http://invalid/rest/api/2/issue?"
                    ),  # Python <3.11 and Windows
                ),
            ],
        )

    @disable_logging
    def test_create_issue_without_url(self):
        """Test that without a URL an error message is returned."""
        issue_tracker = self.issue_tracker(url=URL(""))
        self.assertEqual(("", "Issue tracker has no URL configured."), issue_tracker.create_issue(self.ISSUE_SUMMARY))

    @disable_logging
    @patch("requests.get", Mock(side_effect=OSError))
    @patch("requests.post")
    def test_create_issue_with_exception(self, requests_post):
        """Test that the exception is returned when something goes wrong."""
        requests_post.side_effect = [OSError("Something went wrong")]
        self.assertEqual(("", "Something went wrong"), self.issue_tracker().create_issue(self.ISSUE_SUMMARY))

    @disable_logging
    @patch("requests.get", Mock(side_effect=OSError))
    @patch("requests.post")
    def test_create_issue_with_empty_exception(self, requests_post):
        """Test that the exception is returned when something goes wrong."""
        requests_post.side_effect = [OSError]
        self.assertEqual(("", "OSError"), self.issue_tracker().create_issue(self.ISSUE_SUMMARY))

    @disable_logging
    @patch("requests.get", Mock(side_effect=OSError))
    @patch("requests.post")
    def test_create_issue_with_jira_error_messages(self, requests_post):
        """Test that the error messages returned by Jira are added to the error."""
        response = Mock()
        response.json.return_value = {
            "errorMessages": ["Something is wrong"],
            "errors": {"issuetype": "Specify a valid issue type", "summary": "Summary is required"},
        }
        response.raise_for_status.side_effect = requests.HTTPError("400 Client Error", response=response)
        requests_post.return_value = response
        expected_error = (
            "400 Client Error (Something is wrong; issuetype: Specify a valid issue type; summary: Summary is required)"
        )
        self.assertEqual(("", expected_error), self.issue_tracker().create_issue(self.ISSUE_SUMMARY))

    @disable_logging
    @patch("requests.get", Mock(side_effect=OSError))
    @patch("requests.post")
    def test_create_issue_with_jira_error_without_json(self, requests_post):
        """Test that the error is returned as is if the Jira error response contains no JSON."""
        response = Mock()
        response.json.side_effect = requests.JSONDecodeError("Expecting value", "", 0)
        response.raise_for_status.side_effect = requests.HTTPError("500 Server Error", response=response)
        requests_post.return_value = response
        self.assertEqual(("", "500 Server Error"), self.issue_tracker().create_issue(self.ISSUE_SUMMARY))

    @disable_logging
    @patch("requests.get", Mock(side_effect=OSError))
    @patch("requests.post")
    def test_create_issue_with_jira_error_with_unexpected_json(self, requests_post):
        """Test that the error is returned as is if the Jira error response contains unexpected JSON."""
        response = Mock()
        response.json.return_value = ["unexpected"]
        response.raise_for_status.side_effect = requests.HTTPError("400 Client Error", response=response)
        requests_post.return_value = response
        self.assertEqual(("", "400 Client Error"), self.issue_tracker().create_issue(self.ISSUE_SUMMARY))
