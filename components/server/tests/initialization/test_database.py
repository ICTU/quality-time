"""Unit tests for the database initialization."""

import json
import pathlib
import unittest
from unittest.mock import Mock, call, mock_open, patch

from data_model import DATA_MODEL_JSON
from routes.plugins.auth_plugin import EDIT_ENTITY_PERMISSION, EDIT_REPORT_PERMISSION
from initialization.database import init_database


class DatabaseInitTest(unittest.TestCase):
    """Unit tests for database initialization."""

    IGNORE_ME = "ignore me"

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
        self.database.sessions.find_one.return_value = dict(user="jodoe")
        self.database.measurements.count_documents.return_value = 0
        self.database.measurements.index_information.return_value = {}
        self.mongo_client().quality_time_db = self.database

    def init_database(self, data_model_json: str, assert_glob_called: bool = True) -> None:
        """Initialize the database."""
        with patch.object(pathlib.Path, "glob", Mock(return_value=[])) as glob_mock, patch.object(
            pathlib.Path, "open", mock_open(read_data=data_model_json)
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
        self.database.reports_overviews.insert.assert_called_once()

    def test_init_initialized_database(self):
        """Test the initialization of an initialized database."""
        data_model = json.loads(DATA_MODEL_JSON)
        data_model["_id"] = "id"
        data_model["timestamp"] = "now"
        self.database.datamodels.find_one.return_value = data_model
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
                                    "source2": {"type": "axe_selenium_python", "name": "Don't change the source name"}
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
                                "sources": {"source2": {"type": "axe_core", "name": "Don't change the source name"}},
                            },
                        }
                    }
                }
            },
        )

    def test_remove_notification_frequency(self):
        """Test that the notification frequency field is removed."""
        self.database.reports.find.return_value = [
            {"_id": "1", "subjects": {}, "notification_destinations": {}},
            {
                "_id": "2",
                "subjects": {},
                "notification_destinations": {
                    "notification_destination1": {"frequency": 10},
                    "notification_destination2": {"webhook": "https://www.url.com"},
                },
            },
        ]
        self.init_database("{}")
        self.database.reports.replace_one.assert_called_once_with(
            {"_id": "2"},
            {
                "subjects": {},
                "notification_destinations": {
                    "notification_destination1": {},
                    "notification_destination2": {"webhook": "https://www.url.com"},
                },
            },
        )

    def test_remove_wekan_source(self):
        """Test that the wekan source type is removed."""
        self.database.reports.find.return_value = [
            {"_id": "1", "subjects": {}},
            {"_id": "2", "subjects": {"subject1": {"metrics": {}}}},
            {
                "_id": "3",
                "subjects": {
                    "subject2": {
                        "metrics": {
                            "metric1": {"type": "accessibility", "sources": {}},
                            "metric2": {"type": "accessibility", "sources": {"source1": {"type": "wekan"}}},
                            "metric3": {
                                "type": "accessibility",
                                "sources": {"source2": {"type": "wekan"}, "source3": {"type": self.IGNORE_ME}},
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
                            "metric2": {"type": "accessibility", "sources": {}},
                            "metric3": {"type": "accessibility", "sources": {"source3": {"type": self.IGNORE_ME}}},
                        }
                    }
                }
            },
        )

    def test_remove_random_number_source(self):
        """Test that the random number source type is removed."""
        self.database.reports.find.return_value = [
            {"_id": "1", "subjects": {}},
            {"_id": "2", "subjects": {"subject1": {"metrics": {}}}},
            {
                "_id": "3",
                "subjects": {
                    "subject2": {
                        "metrics": {
                            "metric1": {"type": "accessibility", "sources": {}},
                            "metric2": {"type": "accessibility", "sources": {"source1": {"type": "random"}}},
                            "metric3": {
                                "type": "accessibility",
                                "sources": {"source2": {"type": "random"}, "source3": {"type": self.IGNORE_ME}},
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
                            "metric2": {"type": "accessibility", "sources": {}},
                            "metric3": {"type": "accessibility", "sources": {"source3": {"type": self.IGNORE_ME}}},
                        }
                    }
                }
            },
        )

    def test_migrate_edit_permissions(self):
        """Make sure that permissions are migrated correctly."""
        self.database.reports_overviews.find.return_value = [
            {"_id": "0"},
            {"_id": "1", "editors": []},
            {"_id": "2", "editors": ["admin", "jadoe"]},
        ]
        self.init_database("{}")

        self.assertEqual(self.database.reports_overviews.find.call_count, 1)
        set_default_permissions = {
            "$set": {"permissions": {EDIT_REPORT_PERMISSION: [], EDIT_ENTITY_PERMISSION: []}},
            "$unset": {"editors": ""},
        }
        self.database.reports_overviews.update_one.assert_has_calls(
            [
                call({"_id": "0"}, set_default_permissions),
                call({"_id": "1"}, set_default_permissions),
                call(
                    {"_id": "2"},
                    {
                        "$set": {
                            "permissions": {EDIT_REPORT_PERMISSION: ["admin", "jadoe"], EDIT_ENTITY_PERMISSION: []}
                        },
                        "$unset": {"editors": ""},
                    },
                ),
            ]
        )
