"""Unit tests for database migrations."""

from initialization.migrations import perform_migrations

from tests.base import DataModelTestCase
from tests.fixtures import SourceId, REPORT_ID, SUBJECT_ID, METRIC_ID, METRIC_ID2, METRIC_ID3, SOURCE_ID, SOURCE_ID2


class MigrationTestCase(DataModelTestCase):
    """Base class for migration unit tests."""

    def existing_report(self, metric_type: str):
        """Return a report fixture. To be extended in subclasses."""
        return {
            "_id": "id",
            "report_uuid": REPORT_ID,
            "subjects": {SUBJECT_ID: {"metrics": {METRIC_ID: {"type": metric_type}}}},
        }

    def inserted_report(self, **kwargs):
        """Return a report as it is expected to have been inserted into the reports collection.

        By default, this is the name as the existing report, except for the _id being removed.
        """
        report = self.existing_report(**kwargs)
        del report["_id"]
        return report


class ChangeAccessibilityViolationsTest(MigrationTestCase):
    """Unit tests for the accessibility violations database migration."""

    def existing_report(
        self,
        *,
        metric_type: str = "accessibility",
        metric_name: str = "",
        metric_unit: str = "",
        extra_metrics: bool = False,
    ):
        """Extend to add name and unit to the metric and optional extra metrics."""
        report = super().existing_report(metric_type=metric_type)
        report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["name"] = metric_name
        report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["unit"] = metric_unit
        if extra_metrics:
            report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID2] = {"type": "violations"}
            report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID3] = {"type": "security_warnings"}
        return report

    def inserted_report(
        self, metric_name: str = "Accessibility violations", metric_unit: str = "accessibility violations", **kwargs
    ):
        """Return a report as it is expected to have been inserted into the reports collection."""
        return super().inserted_report(
            metric_type="violations", metric_name=metric_name, metric_unit=metric_unit, **kwargs
        )

    def test_no_reports(self):
        """Test that the migration succeeds without reports."""
        self.database.reports.find.return_value = []
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_report_without_accessibility_metrics(self):
        """Test that the migration succeeds with reports, but without accessibility metrics."""
        self.database.reports.find.return_value = [self.existing_report(metric_type="loc")]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_report_with_accessibility_metric(self):
        """Test that the migration succeeds with an accessibility metric."""
        self.database.reports.find.return_value = [self.existing_report()]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_called_once_with({"_id": "id"}, self.inserted_report())

    def test_accessibility_metric_with_name_and_unit(self):
        """Test that the migration succeeds with an accessibility metric, and existing name and unit are kept."""
        self.database.reports.find.return_value = [self.existing_report(metric_name="name", metric_unit="unit")]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_called_once_with(
            {"_id": "id"},
            self.inserted_report(metric_name="name", metric_unit="unit"),
        )

    def test_report_with_accessibility_metric_and_other_types(self):
        """Test that the migration succeeds with an accessibility metric and other metric types."""
        self.database.reports.find.return_value = [self.existing_report(extra_metrics=True)]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_called_once_with(
            {"_id": "id"},
            self.inserted_report(extra_metrics=True),
        )


class BranchParameterTest(MigrationTestCase):
    """Unit tests for the branch parameter database migration."""

    def existing_report(
        self, metric_type: str = "loc", sources: dict[SourceId, dict[str, str | dict[str, str]]] | None = None
    ):
        """Extend to add sources and an extra metric without sources."""
        report = super().existing_report(metric_type=metric_type)
        report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID2] = {"type": "issues"}
        if sources:
            report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"] = sources
        return report

    def test_no_reports(self):
        """Test that the migration succeeds without reports."""
        self.database.reports.find.return_value = []
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_report_without_branch_parameter(self):
        """Test that the migration succeeds with reports, but without metrics with a branch parameter."""
        self.database.reports.find.return_value = [self.existing_report()]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_report_with_non_empty_branch_parameter(self):
        """Test that the migration succeeds when the branch parameter is not empty."""
        self.database.reports.find.return_value = [
            self.existing_report(sources={SOURCE_ID: {"type": "sonarqube", "parameters": {"branch": "main"}}})
        ]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_report_with_branch_parameter_without_value(self):
        """Test that the migration succeeds when a source has an empty branch parameter."""
        sources = {
            SOURCE_ID: {"type": "gitlab", "parameters": {"branch": ""}},
            SOURCE_ID2: {"type": "cloc", "parameters": {"branch": ""}},
        }
        report = self.existing_report(metric_type="source_up_to_dateness", sources=sources)
        self.database.reports.find.return_value = [report]
        perform_migrations(self.database)
        inserted_sources = {
            SOURCE_ID: {"type": "gitlab", "parameters": {"branch": "master"}},
            SOURCE_ID2: {"type": "cloc", "parameters": {"branch": ""}},
        }
        inserted_report = self.inserted_report(metric_type="source_up_to_dateness", sources=inserted_sources)
        self.database.reports.replace_one.assert_called_once_with({"_id": "id"}, inserted_report)
