"""Unit tests for the database initialization."""

import pathlib
from unittest.mock import Mock, mock_open, patch

from initialization.database import init_database, perform_migrations

from tests.base import DataModelTestCase


class DatabaseInitTest(DataModelTestCase):
    """Unit tests for database initialization."""

    def setUp(self):
        """Override to set up the database fixture."""
        self.mongo_client = Mock()
        self.database = Mock()
        self.database.reports.find.return_value = []
        self.database.reports.distinct.return_value = []
        self.database.datamodels.find_one.return_value = None
        self.database.reports_overviews.find_one.return_value = None
        self.database.reports_overviews.find.return_value = []
        self.database.reports.count_documents.return_value = 0
        self.database.sessions.find_one.return_value = {"user": "jodoe"}
        self.database.measurements.count_documents.return_value = 0
        self.database.measurements.index_information.return_value = {}
        self.mongo_client().quality_time_db = self.database

    def init_database(self, data_model_json: str, assert_glob_called: bool = True) -> None:
        """Initialize the database."""
        with patch.object(pathlib.Path, "glob", Mock(return_value=[])) as glob_mock, patch.object(
            pathlib.Path,
            "open",
            mock_open(read_data=data_model_json),
        ), patch("pymongo.MongoClient", self.mongo_client):
            init_database()
        if assert_glob_called:
            glob_mock.assert_called()
        else:
            glob_mock.assert_not_called()

    def test_init_empty_database(self):
        """Test the initialization of an empty database."""
        self.init_database('{"change": "yes"}')
        self.database.datamodels.insert_one.assert_called_once()
        self.database.reports_overviews.insert_one.assert_called_once()

    def test_init_initialized_database(self):
        """Test the initialization of an initialized database."""
        self.database.datamodels.find_one.return_value = self.DATA_MODEL
        self.database.reports_overviews.find_one.return_value = {"_id": "id"}
        self.database.reports.count_documents.return_value = 10
        self.database.measurements.count_documents.return_value = 20
        self.init_database("{}")
        self.database.datamodels.insert_one.assert_not_called()
        self.database.reports_overviews.insert_one.assert_not_called()

    def test_skip_loading_example_reports(self):
        """Test that loading example reports can be skipped."""
        with patch("src.initialization.database.os.environ.get", Mock(return_value="False")):
            self.init_database('{"change": "yes"}', False)
        self.database.datamodels.insert_one.assert_called_once()
        self.database.reports_overviews.insert_one.assert_called_once()


class DatabaseMigrationsTest(DataModelTestCase):
    """Unit tests for the database migration."""

    def setUp(self):
        """Override to set up the database fixture."""
        self.database = Mock()

    def test_change_accessibility_violations_to_violations_without_reports(self):
        """Test that the migration succeeds without reports."""
        self.database.reports.find.return_value = []
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_change_accessibility_violations_to_violations_when_report_has_no_accessibility_metrics(self):
        """Test that the migration succeeds wtih reports, but without accessibility metrics."""
        self.database.reports.find.return_value = [
            {"report_uuid": "report_uuid", "subjects": {"subject_uuid": {"metrics": {"metric_uuid": {"type": "loc"}}}}}
        ]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_not_called()

    def test_change_accessibility_violations_to_violations_when_report_has_an_accessibility_metric(self):
        """Test that the migration succeeds with an accessibility metric."""
        self.database.reports.find.return_value = [
            {
                "_id": "id",
                "report_uuid": "report_uuid",
                "subjects": {"subject_uuid": {"metrics": {"metric_uuid": {"type": "accessibility"}}}},
            },
        ]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_called_once_with(
            {"_id": "id"},
            {
                "report_uuid": "report_uuid",
                "subjects": {
                    "subject_uuid": {
                        "metrics": {
                            "metric_uuid": {
                                "type": "violations",
                                "name": "Accessibility violations",
                                "unit": "accessibility violations",
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
                "report_uuid": "report_uuid",
                "subjects": {
                    "subject_uuid": {
                        "metrics": {
                            "metric_uuid": {"type": "accessibility"},
                            "metric_uuid2": {"type": "violations"},
                            "metric_uuid3": {"type": "security_warnings"},
                        }
                    }
                },
            }
        ]
        perform_migrations(self.database)
        self.database.reports.replace_one.assert_called_once_with(
            {"_id": "id"},
            {
                "report_uuid": "report_uuid",
                "subjects": {
                    "subject_uuid": {
                        "metrics": {
                            "metric_uuid": {
                                "type": "violations",
                                "name": "Accessibility violations",
                                "unit": "accessibility violations",
                            },
                            "metric_uuid2": {
                                "type": "violations",
                            },
                            "metric_uuid3": {
                                "type": "security_warnings",
                            },
                        }
                    }
                },
            },
        )
