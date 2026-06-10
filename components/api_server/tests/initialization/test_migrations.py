"""Unit tests for database migrations."""

from initialization.migrations import perform_migrations

from tests.base import DataModelTestCase
from tests.fixtures import METRIC_ID, METRIC_ID2, METRIC_ID3, REPORT_ID, SOURCE_ID, SOURCE_ID2, SUBJECT_ID


class MigrationTestCase(DataModelTestCase):
    """Base class for migration unit tests."""

    def set_database_reports(self, *reports) -> None:
        """Make the database return the given reports, taking the find filter into account."""

        def find(filter=None, **kwargs) -> list:  # noqa: A002, ARG001
            """Return the reports that match the filter."""
            if filter == {"source_locations": {"$exists": False}}:
                return [report for report in reports if "source_locations" not in report]
            return [report for report in reports if report.get("last", True) and "deleted" not in report]

        self.database.reports.find.side_effect = find

    def existing_report(self, **kwargs):
        """Return a report fixture. To be extended in subclasses."""
        return {
            "_id": "id",
            "report_uuid": REPORT_ID,
            "source_locations": {},
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
        self.set_database_reports()
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_empty_reports(self):
        """Test that the migrations succeed when the report does not have anything to migrate."""
        self.set_database_reports({"report_uuid": REPORT_ID, "source_locations": {}, "subjects": {}})
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()


class RemoveAdditionTest(MigrationTestCase):
    """Unit tests for the migration to remove addition fields from metrics."""

    def test_report_without_addition_fields(self):
        """Test that the migrations succeed with reports, but without addition fields."""
        self.set_database_reports(self.existing_report())
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_report_with_addition_fields(self):
        """Test that the migrations succeed with reports that have metrics with addition fields."""
        self.set_database_reports(self.existing_report(addition="min"))
        perform_migrations(self.database)
        self.check_inserted_report(self.inserted_report())


class RemoveCheckmarxTest(MigrationTestCase):
    """Init tests for the migration to remove Checkmarx sources from metrics."""

    def existing_report(self, **kwargs):
        """Extend to add Checkmarx source."""
        report = super().existing_report(**kwargs)
        metrics = report["subjects"][SUBJECT_ID]["metrics"]
        metrics[METRIC_ID2] = {"type": "security_warnings", "sources": {SOURCE_ID: {"type": "cxsast"}}}
        metrics[METRIC_ID3] = {"type": "security_warnings", "sources": {SOURCE_ID2: {"type": "sonarqube"}}}
        return report

    def test_report_without_checkmarx(self):
        """Test that the migration succeeds with reports without Checkmarx sources."""
        self.set_database_reports(super().existing_report())
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_report_with_checkmarx(self):
        """Test that the migration succeeds with reports without Checkmarx sources."""
        self.set_database_reports(self.existing_report())
        perform_migrations(self.database)
        inserted_report = self.inserted_report()
        del inserted_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID2]["sources"][SOURCE_ID]
        self.check_inserted_report(inserted_report)


class RemoveSubjectDescriptionTest(MigrationTestCase):
    """Unit tests for the migration to remove description fields from subjects."""

    def existing_report(self, **kwargs):
        """Extend to add description to subject."""
        report = super().existing_report(**kwargs)
        report["subjects"][SUBJECT_ID]["description"] = "A custom software application or component."
        return report

    def test_report_without_subject_description(self):
        """Test that the migration succeeds with reports without subject descriptions."""
        self.set_database_reports(super().existing_report())
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_report_with_subject_description(self):
        """Test that the migration succeeds with reports that have subject descriptions."""
        self.set_database_reports(self.existing_report())
        perform_migrations(self.database)
        inserted_report = self.inserted_report()
        del inserted_report["subjects"][SUBJECT_ID]["description"]
        self.check_inserted_report(inserted_report)


class AddSourceLocationsTest(MigrationTestCase):
    """Unit tests for the migration to add source locations to reports."""

    def existing_report(self, **kwargs):
        """Override to return an old-structure report without source locations."""
        return {
            "_id": "id",
            "report_uuid": REPORT_ID,
            "subjects": {
                SUBJECT_ID: {
                    "type": "software",
                    "metrics": {
                        METRIC_ID: {
                            "type": "violations",
                            "sources": {
                                SOURCE_ID: {
                                    "type": "sonarqube",
                                    "name": "Source",
                                    "parameters": {"url": "https://url", "password": "password"},  # nosec
                                },
                                **kwargs.get("extra_sources", {}),
                            },
                        },
                    },
                },
            },
            **{key: value for key, value in kwargs.items() if key != "extra_sources"},
        }

    def inserted_source_location(self):
        """Return the source location as expected to be added to the migrated report."""
        return {
            "location_name": "Source",
            "source_type": "sonarqube",
            "url": "https://url",
            "landing_url": "",
            "username": "",
            "password": "password",  # nosec
            "private_token": "",
        }

    def test_report_without_source_locations(self):
        """Test that the migration adds source locations to old-structure reports."""
        self.set_database_reports(self.existing_report())
        perform_migrations(self.database)
        inserted_report = self.database.reports.replace_one.call_args[0][1]
        location_uuid, location = next(iter(inserted_report["source_locations"].items()))
        self.assertEqual(self.inserted_source_location(), location)
        source = inserted_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"][SOURCE_ID]
        self.assertEqual(location_uuid, source["source_location"])
        self.assertEqual({}, source["parameters"])

    def test_report_with_equal_source_locations(self):
        """Test that sources with the same name, type, and location parameters share one source location."""
        extra_source = {
            "type": "sonarqube",
            "name": "Source",
            "parameters": {"url": "https://url", "password": "password"},  # nosec
        }
        self.set_database_reports(self.existing_report(extra_sources={SOURCE_ID2: extra_source}))
        perform_migrations(self.database)
        inserted_report = self.database.reports.replace_one.call_args[0][1]
        self.assertEqual(1, len(inserted_report["source_locations"]))
        sources = inserted_report["subjects"][SUBJECT_ID]["metrics"][METRIC_ID]["sources"]
        self.assertEqual(sources[SOURCE_ID]["source_location"], sources[SOURCE_ID2]["source_location"])

    def test_report_with_source_locations_is_skipped(self):
        """Test that reports that already have source locations are not migrated again."""
        self.set_database_reports(self.existing_report(source_locations={}))
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_deleted_and_non_last_reports_are_migrated(self):
        """Test that deleted reports and old versions of reports are migrated too."""
        deleted_report = self.existing_report(deleted="true")
        non_last_report = self.existing_report(last=False)
        non_last_report["_id"] = "id2"
        self.set_database_reports(deleted_report, non_last_report)
        perform_migrations(self.database)
        self.assertEqual(2, self.database.reports.replace_one.call_count)
        for call_args in self.database.reports.replace_one.call_args_list:
            self.assertIn("source_locations", call_args[0][1])

    def test_migration_uses_filter_for_all_documents(self):
        """Test that the migration queries all report documents without source locations."""
        self.set_database_reports()
        perform_migrations(self.database)
        self.database.reports.find.assert_any_call(filter={"source_locations": {"$exists": False}})
