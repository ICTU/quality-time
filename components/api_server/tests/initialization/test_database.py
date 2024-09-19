"""Unit tests for the database initialization."""

import pathlib
from unittest.mock import Mock, mock_open, patch

from initialization.database import init_database

from tests.base import DataModelTestCase


class DatabaseInitTest(DataModelTestCase):
    """Unit tests for database initialization."""

    def setUp(self):
        """Extend to set up the Mongo client and database contents."""
        super().setUp()
        self.mongo_client = Mock()
        self.database.reports.find.return_value = []
        self.database.reports.distinct.return_value = []
        self.database.datamodels.find_one.return_value = None
        self.database.reports_overviews.find_one.return_value = None
        self.database.reports_overviews.find.return_value = []
        self.database.reports.count_documents.return_value = 0
        self.database.sessions.find_one.return_value = {"user": "jodoe"}
        self.database.measurements.count_documents.return_value = 0
        self.database.measurements.index_information.return_value = {}
        self.mongo_client.get_database.return_value = self.database

    def init_database(self, data_model_json: str, assert_glob_called: bool = True) -> None:
        """Initialize the database."""
        with (
            patch.object(pathlib.Path, "glob", Mock(return_value=[])) as glob_mock,
            patch.object(
                pathlib.Path,
                "open",
                mock_open(read_data=data_model_json),
            ),
        ):
            init_database(self.mongo_client)
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
