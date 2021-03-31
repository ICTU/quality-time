"""Unit tests for the database initialization."""

import pathlib
import unittest
from unittest.mock import Mock, mock_open, patch

from initialization.database import init_database


class DatabaseInitTest(unittest.TestCase):
    """Unit tests for database initialization."""

    def setUp(self):
        """Override to set up the database fixture."""
        self.mongo_client = Mock()
        self.database = Mock()
        self.database.reports.find.return_value = []
        self.database.reports.distinct.return_value = []
        self.database.datamodels.find_one.return_value = None
        self.database.reports_overviews.find_one.return_value = None
        self.database.reports.count_documents.return_value = 0
        self.database.sessions.find_one.return_value = dict(user="jodoe")
        self.database.measurements.count_documents.return_value = 0
        self.mongo_client().quality_time_db = self.database

    def init_database(self, data_model_json: str, assert_glob_called: bool = True) -> None:
        """Initialize the database."""
        with patch.object(pathlib.Path, "glob", Mock(return_value=[])) as glob_mock:
            with patch.object(pathlib.Path, "open", mock_open(read_data=data_model_json)):
                with patch("pymongo.MongoClient", self.mongo_client):
                    init_database()
        if assert_glob_called:
            glob_mock.assert_called()
        else:
            glob_mock.assert_not_called()

    def test_init_empty_database(self):
        """Test the initialization of an empty database."""
        self.init_database('{"change": "yes"}')
        self.database.datamodels.insert_one.assert_called_once()
        self.database.reports_overviews.insert.assert_called_once()

    def test_init_initialized_database(self):
        """Test the initialization of an initialized database."""
        self.database.datamodels.find_one.return_value = dict(_id="id", timestamp="now")
        self.database.reports_overviews.find_one.return_value = dict(_id="id")
        self.database.reports.count_documents.return_value = 10
        self.database.measurements.count_documents.return_value = 20
        self.init_database("{}")
        self.database.datamodels.insert_one.assert_not_called()
        self.database.reports_overviews.insert.assert_not_called()

    def test_skip_loading_example_reports(self):
        """Test that loading example reports can be skipped."""
        with patch("src.initialization.database.os.environ.get", Mock(return_value="False")):
            self.init_database('{"change": "yes"}', False)
        self.database.datamodels.insert_one.assert_called_once()
        self.database.reports_overviews.insert.assert_called_once()

    def test_add_last_flag_to_reports(self):
        """Test that the last flag is added to reports."""
        self.database.reports.distinct.return_value = ["report_uuid"]
        self.database.reports.find_one.return_value = {"_id": "1"}
        self.init_database("{}")
        self.database.reports.update_many.assert_called_once()

    def test_rename_ready_user_story_points(self):
        """Test that the ready user story points metric is correctly renamed."""
        self.database.reports.find.return_value = [
            {"_id": "1", "subjects": {}},
            {"_id": "2", "subjects": {"subject1": {"metrics": {}}}},
            {
                "_id": "3",
                "subjects": {
                    "subject2": {
                        "metrics": {
                            "metric1": {"type": "violations"},
                            "metric2": {"type": "ready_user_story_points"},
                            "metric3": {"type": "ready_user_story_points", "name": "Don't change the name"},
                        }
                    }
                },
            },
        ]
        self.init_database("{}")
        self.database.reports.replace_one.assert_called_once_with(
            {"_id": "3"},
            {
                "subjects": {
                    "subject2": {
                        "metrics": {
                            "metric1": {"type": "violations"},
                            "metric2": {"type": "user_story_points", "name": "Ready user story points"},
                            "metric3": {"type": "user_story_points", "name": "Don't change the name"},
                        }
                    }
                }
            },
        )

    def test_rename_teams_webhook_notification_destination(self):
        """Test that the teams_webhook notification destination is correctly renamed."""
        self.database.reports.find.return_value = [
            {"_id": "1", "subjects": {}, "notification_destinations": {}},
            {
                "_id": "2",
                "subjects": {},
                "notification_destinations": {
                    "notification_destination1": {"Do_not_change_me": "Don't change me either"},
                    "notification_destination2": {"teams_webhook": "https://www.url1.com"},
                    "notification_destination3": {"webhook": "https://www.url2.com"},
                },
            },
        ]

        self.init_database("{}")
        self.database.reports.replace_one.assert_called_once_with(
            {"_id": "2"},
            {
                "subjects": {},
                "notification_destinations": {
                    "notification_destination1": {"Do_not_change_me": "Don't change me either"},
                    "notification_destination2": {"webhook": "https://www.url1.com"},
                    "notification_destination3": {"webhook": "https://www.url2.com"},
                },
            },
        )

    def test_rename_axe_selenium_python(self):
        """Test that the axe-selenium-python source type is renamed to axe_core."""
        self.database.reports.find.return_value = [
            {"_id": "1", "subjects": {}},
            {"_id": "2", "subjects": {"subject1": {"metrics": {}}}},
            {
                "_id": "3",
                "subjects": {
                    "subject2": {
                        "metrics": {
                            "metric1": {"type": "accessibility", "sources": {}},
                            "metric2": {
                                "type": "accessibility",
                                "sources": {"source1": {"type": "axe_selenium_python"}},
                            },
                            "metric3": {
                                "type": "accessibility",
                                "sources": {
                                    "source2": {"type": "axe_selenium_python", "name": "Don't change the name"}
                                },
                            },
                        }
                    }
                },
            },
        ]
        self.init_database("{}")
        self.database.reports.replace_one.assert_called_once_with(
            {"_id": "3"},
            {
                "subjects": {
                    "subject2": {
                        "metrics": {
                            "metric1": {"type": "accessibility", "sources": {}},
                            "metric2": {
                                "type": "accessibility",
                                "sources": {"source1": {"type": "axe_core", "name": "axe-selenium-python"}},
                            },
                            "metric3": {
                                "type": "accessibility",
                                "sources": {"source2": {"type": "axe_core", "name": "Don't change the name"}},
                            },
                        }
                    }
                }
            },
        )
