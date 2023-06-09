"""Model transformation unit tests."""

from model.transformations import hide_credentials, CREDENTIALS_REPLACEMENT_TEXT

from tests.base import DataModelTestCase
from tests.fixtures import create_report, SUBJECT_ID, METRIC_ID, SOURCE_ID


class HideCredentialsTest(DataModelTestCase):
    """Unit tests for the hide credentials transformation."""

    def setUp(self) -> None:
        """Override to set up the report fixture."""
        self.report = create_report()
        self.source_parameters = self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID][
            "parameters"
        ]
        self.issue_tracker_parameters = self.report["issue_tracker"]["parameters"]

    def test_hide_source_credentials(self):
        """Test that the source credentials are hidden."""
        hide_credentials(self.DATA_MODEL, self.report)
        self.assertEqual(CREDENTIALS_REPLACEMENT_TEXT, self.source_parameters["password"])

    def test_hide_issue_tracker_credentials(self):
        """Test that the issue tracker credentials are hidden."""
        hide_credentials(self.DATA_MODEL, self.report)
        self.assertEqual(CREDENTIALS_REPLACEMENT_TEXT, self.issue_tracker_parameters["password"])

    def test_do_not_hide_empty_source_credentials(self):
        """Test that empty source credentials are not replaced with a placeholder.

        This is needed because users cannot see the difference between a masked credential and a masked empty
        credential in the UI. If we mask empty credentials the users won't be able to tell that they did successfully
        clear a credential (because it looks the same as an existing credential) and complain there is a bug.
        """
        self.source_parameters["password"] = ""
        hide_credentials(self.DATA_MODEL, self.report)
        self.assertEqual("", self.source_parameters["password"])

    def test_do_not_hide_empty_issue_tracker_credentials(self):
        """Test that empty issue tracker credentials are not replaced with a placeholder.

        This is needed because users cannot see the difference between a masked credential and a masked empty
        credential in the UI. If we mask empty credentials the users won't be able to tell that they did successfully
        clear a credential (because it looks the same as an existing credential) and complain there is a bug.
        """
        self.issue_tracker_parameters["private_token"] = ""
        hide_credentials(self.DATA_MODEL, self.report)
        self.assertEqual("", self.issue_tracker_parameters["private_token"])
