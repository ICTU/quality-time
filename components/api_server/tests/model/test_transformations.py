"""Model transformation unit tests."""

from model.report import Report
from model.transformations import change_source_parameter, hide_credentials, CREDENTIALS_REPLACEMENT_TEXT

from tests.base import DataModelTestCase
from tests.fixtures import create_report, METRIC_ID2, SUBJECT_ID, METRIC_ID, REPORT_ID, SOURCE_ID, SOURCE_ID2
from utils.type import SourceContext


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
        self.source_parameters["password"] = ""  # nosec
        hide_credentials(self.DATA_MODEL, self.report)
        self.assertEqual("", self.source_parameters["password"])

    def test_do_not_hide_empty_issue_tracker_credentials(self):
        """Test that empty issue tracker credentials are not replaced with a placeholder.

        This is needed because users cannot see the difference between a masked credential and a masked empty
        credential in the UI. If we mask empty credentials the users won't be able to tell that they did successfully
        clear a credential (because it looks the same as an existing credential) and complain there is a bug.
        """
        self.issue_tracker_parameters["private_token"] = ""  # nosec
        hide_credentials(self.DATA_MODEL, self.report)
        self.assertEqual("", self.issue_tracker_parameters["private_token"])


class ChangeSourceParameterTest(DataModelTestCase):
    """Unit tests for the change source parameter transformation."""

    def test_change_one_url(self):
        """Test changing the URL parameter."""
        report = Report(self.DATA_MODEL, create_report())
        subject = report.subjects_dict[SUBJECT_ID]
        metric = report.metrics_dict[METRIC_ID]
        source = metric.sources_dict[SOURCE_ID]
        context = SourceContext(source=source, metric=metric, subject=subject, report=report)
        changed_ids, changed_source_ids = change_source_parameter(
            [report], context, "url", "https://url", "https://new", "source"
        )
        self.assertEqual([REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID], changed_ids)
        self.assertEqual({SOURCE_ID}, changed_source_ids)

    def test_change_multiple_urls(self):
        """Test changing the URL parameter for two sources."""
        report_dict = create_report()
        report_dict["subjects"][SUBJECT_ID]["metrics"][METRIC_ID2] = {
            "name": "Metric 2",
            "type": "violations",
            "sources": {
                SOURCE_ID2: {
                    "type": "sonarqube",
                    "parameters": {"url": "https://url"},
                },
            },
        }
        report = Report(self.DATA_MODEL, report_dict)
        subject = report.subjects_dict[SUBJECT_ID]
        metric = report.metrics_dict[METRIC_ID]
        source = metric.sources_dict[SOURCE_ID]
        context = SourceContext(source=source, metric=metric, subject=subject, report=report)
        changed_ids, changed_source_ids = change_source_parameter(
            [report], context, "url", "https://url", "https://2", "subject"
        )
        self.assertEqual([REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID, METRIC_ID2, SOURCE_ID2], changed_ids)
        self.assertEqual({SOURCE_ID, SOURCE_ID2}, changed_source_ids)

    def test_change_parameter_that_depends_on_metric_type(self):
        """Test that a parameter that depends on the metric type is not changed when the metric type is different."""
        report_dict = create_report()
        # Add a second metric that has a different type, but the same source type as the first metric:
        report_dict["subjects"][SUBJECT_ID]["metrics"][METRIC_ID2] = {
            "name": "Metric 2",
            "type": "remediation_effort",
            "sources": {
                SOURCE_ID2: {
                    "type": "sonarqube",
                    "parameters": {"url": "https://url"},
                },
            },
        }
        report = Report(self.DATA_MODEL, report_dict)
        subject = report.subjects_dict[SUBJECT_ID]
        metric = report.metrics_dict[METRIC_ID]
        source = metric.sources_dict[SOURCE_ID]
        context = SourceContext(source=source, metric=metric, subject=subject, report=report)
        changed_ids, changed_source_ids = change_source_parameter(
            [report], context, "tags", ["security"], [], "subject"
        )
        self.assertEqual([REPORT_ID, SUBJECT_ID, METRIC_ID, SOURCE_ID], changed_ids)
        self.assertEqual({SOURCE_ID}, changed_source_ids)
