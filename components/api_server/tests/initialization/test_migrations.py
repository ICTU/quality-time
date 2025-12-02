"""Unit tests for database migrations."""

from initialization.migrations import perform_migrations

from tests.base import DataModelTestCase
from tests.fixtures import REPORT_ID, SUBJECT_ID, METRIC_ID


class MigrationTestCase(DataModelTestCase):
    """Base class for migration unit tests."""

    def existing_report(self, **kwargs):
        """Return a report fixture. To be extended in subclasses."""
        return {
            "_id": "id",
            "report_uuid": REPORT_ID,
            "subjects": {SUBJECT_ID: {"type": "software", "metrics": {METRIC_ID: {"type": "tests", **kwargs}}}},
        }

    def inserted_report(self, **kwargs):
        """Return a report as it is expected to have been inserted into the reports collection.

        By default, this is the same as the existing report, except for the _id being removed.
        """
        report = self.existing_report(**kwargs)
        del report["_id"]
        return report

    def check_inserted_report(self, inserted_report):
        """Check that the report was inserted."""
        self.database.reports.replace_one.assert_called_once_with({"_id": "id"}, inserted_report)


class NoOpMigrationTest(MigrationTestCase):
    """Unit tests for empty database and empty reports."""

    def test_no_reports(self):
        """Test that the migrations succeed without reports."""
        self.database.reports.find.return_value = []
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_empty_reports(self):
        """Test that the migrations succeed when the report does not have anything to migrate."""
        self.database.reports.find.return_value = [{"report_uuid": REPORT_ID, "subjects": {}}]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()


class RemoveAdditionTest(MigrationTestCase):
    """Unit tests for the migration to remove addition fields from metrics."""

    def test_report_without_addition_fields(self):
        """Test that the migrations succeed with reports, but without addition fields."""
        self.database.reports.find.return_value = [self.existing_report()]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_report_with_addition_fields(self):
        """Test that the migrations succeed with reports that have metrics with addition fields."""
        self.database.reports.find.return_value = [self.existing_report(addition="min")]
        perform_migrations(self.database)
        self.check_inserted_report(self.inserted_report())
