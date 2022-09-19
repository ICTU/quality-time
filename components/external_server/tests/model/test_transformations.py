"""Model transformation unit tests."""

from model.transformations import hide_credentials, CREDENTIALS_REPLACEMENT_TEXT

from ..base import DataModelTestCase
from ..fixtures import create_report, SUBJECT_ID, METRIC_ID, SOURCE_ID


class HideCredentialsTest(DataModelTestCase):
    """Unit tests for the hide credentials transformation."""

    def setUp(self) -> None:
        """Override to set up the report fixture."""
        self.report = create_report()

    def test_hide_issue_tracker_credentials(self):
        """Test that the issue tracker credentials are hidden."""
        hide_credentials(self.DATA_MODEL, self.report)
        self.assertEqual(CREDENTIALS_REPLACEMENT_TEXT, self.report["issue_tracker"]["parameters"]["password"])

    def test_hide_source_credentials(self):
        """Test that the source credentials are hidden."""
        hide_credentials(self.DATA_MODEL, self.report)
        self.assertEqual(
            CREDENTIALS_REPLACEMENT_TEXT,
            self.report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]["parameters"]["password"],
        )

    def test_do_not_hide_empty_issue_tracker_credentials(self):
        """Test that empty issue tracker credentials are not replaced with a placeholder.

        This is needed because users cannot see the difference between a masked credential and a masked empty
        credential, so otherwise they won't know whether they have cleared a credentials.
        """
        issue_tracker_parameters = self.report["issue_tracker"]["parameters"]
        issue_tracker_parameters["private_token"] = ""
        hide_credentials(self.DATA_MODEL, self.report)
        self.assertEqual("", issue_tracker_parameters["private_token"])
