"""Unit tests for database migrations."""

from initialization.database import perform_migrations

from tests.base import DataModelTestCase
from tests.fixtures import REPORT_ID, SUBJECT_ID, METRIC_ID, METRIC_ID2, METRIC_ID3, SOURCE_ID, SOURCE_ID2


class DatabaseMigrationsChangeAccessibilityViolationsTest(DataModelTestCase):
    """Unit tests for the accessibility violations database migration."""

    def test_change_accessibility_violations_to_violations_without_reports(self):
        """Test that the migration succeeds without reports."""
        self.database.reports.find.return_value = []
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_change_accessibility_violations_to_violations_when_report_has_no_accessibility_metrics(self):
        """Test that the migration succeeds wtih reports, but without accessibility metrics."""
        self.database.reports.find.return_value = [
            {"report_uuid": REPORT_ID, "subjects": {SUBJECT_ID: {"metrics": {METRIC_ID: {"type": "loc"}}}}}
        ]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_change_accessibility_violations_to_violations_when_report_has_an_accessibility_metric(self):
        """Test that the migration succeeds with an accessibility metric."""
        self.database.reports.find.return_value = [
            {
                "_id": "id",
                "report_uuid": REPORT_ID,
                "subjects": {SUBJECT_ID: {"metrics": {METRIC_ID: {"type": "accessibility"}}}},
            },
        ]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_called_once_with(
            {"_id": "id"},
            {
                "report_uuid": REPORT_ID,
                "subjects": {
                    SUBJECT_ID: {
                        "metrics": {
                            METRIC_ID: {
                                "type": "violations",
                                "name": "Accessibility violations",
                                "unit": "accessibility violations",
                            }
                        }
                    }
                },
            },
        )

    def test_change_accessibility_violations_to_violations_when_metric_has_name_and_unit(self):
        """Test that the migration succeeds with an accessibility metric, and existing name and unit are kept."""
        self.database.reports.find.return_value = [
            {
                "_id": "id",
                "report_uuid": REPORT_ID,
                "subjects": {
                    SUBJECT_ID: {"metrics": {METRIC_ID: {"type": "accessibility", "name": "name", "unit": "unit"}}},
                },
            },
        ]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_called_once_with(
            {"_id": "id"},
            {
                "report_uuid": REPORT_ID,
                "subjects": {
                    SUBJECT_ID: {
                        "metrics": {
                            METRIC_ID: {
                                "type": "violations",
                                "name": "name",
                                "unit": "unit",
                            }
                        }
                    }
                },
            },
        )

    def test_change_accessibility_violations_to_violations_when_report_has_accessibility_metric_and_other_types(self):
        """Test that the migration succeeds with an accessibility metric and other metric types."""
        self.database.reports.find.return_value = [
            {
                "_id": "id",
                "report_uuid": REPORT_ID,
                "subjects": {
                    SUBJECT_ID: {
                        "metrics": {
                            METRIC_ID: {"type": "accessibility"},
                            METRIC_ID2: {"type": "violations"},
                            METRIC_ID3: {"type": "security_warnings"},
                        }
                    }
                },
            }
        ]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_called_once_with(
            {"_id": "id"},
            {
                "report_uuid": REPORT_ID,
                "subjects": {
                    SUBJECT_ID: {
                        "metrics": {
                            METRIC_ID: {
                                "type": "violations",
                                "name": "Accessibility violations",
                                "unit": "accessibility violations",
                            },
                            METRIC_ID2: {
                                "type": "violations",
                            },
                            METRIC_ID3: {
                                "type": "security_warnings",
                            },
                        }
                    }
                },
            },
        )


class DatabaseMigrationsBranchParameterTest(DataModelTestCase):
    """Unit tests for the branch parameter database migration."""

    def test_migration_without_reports(self):
        """Test that the migration succeeds without reports."""
        self.database.reports.find.return_value = []
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_migration_when_report_has_no_metrics_with_sources_with_branch_parameter(self):
        """Test that the migration succeeds with reports, but without metrics with a branch parameter."""
        self.database.reports.find.return_value = [
            {
                "report_uuid": REPORT_ID,
                "subjects": {
                    SUBJECT_ID: {
                        "metrics": {
                            METRIC_ID: {"type": "issues"},
                            METRIC_ID2: {"type": "loc"},
                        },
                    },
                },
            },
        ]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_migration_when_report_has_source_with_branch(self):
        """Test that the migration succeeds when the branch parameter is not empty."""
        self.database.reports.find.return_value = [
            {
                "report_uuid": REPORT_ID,
                "subjects": {
                    SUBJECT_ID: {
                        "metrics": {
                            METRIC_ID: {
                                "type": "loc",
                                "sources": {SOURCE_ID: {"type": "sonarqube", "parameters": {"branch": "main"}}},
                            },
                        },
                    },
                },
            },
        ]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_migration_when_report_has_sonarqube_metric_with_branch_without_value(self):
        """Test that the migration succeeds when a source has an empty branch parameter."""
        self.database.reports.find.return_value = [
            {
                "_id": "id",
                "report_uuid": REPORT_ID,
                "subjects": {
                    SUBJECT_ID: {
                        "metrics": {
                            METRIC_ID: {
                                "type": "source_up_to_dateness",
                                "sources": {
                                    SOURCE_ID: {"type": "gitlab", "parameters": {"branch": ""}},
                                    SOURCE_ID2: {"type": "cloc", "parameters": {"branch": ""}},
                                },
                            },
                        },
                    },
                },
            },
        ]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_called_once_with(
            {"_id": "id"},
            {
                "report_uuid": REPORT_ID,
                "subjects": {
                    SUBJECT_ID: {
                        "metrics": {
                            METRIC_ID: {
                                "type": "source_up_to_dateness",
                                "sources": {
                                    SOURCE_ID: {"type": "gitlab", "parameters": {"branch": "master"}},
                                    SOURCE_ID2: {"type": "cloc", "parameters": {"branch": ""}},
                                },
                            },
                        },
                    },
                },
            },
        )
