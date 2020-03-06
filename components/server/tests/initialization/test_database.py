"""Unit tests for the database initialization."""

import unittest
import pathlib
from unittest.mock import Mock, mock_open, patch

import bottle

from initialization.database import init_database


class DatabaseInitTest(unittest.TestCase):
    """Unit tests for database initialization."""

    def setUp(self):
        self.mongo_client = Mock()
        self.database = Mock()
        self.database.reports.find.return_value = []
        self.database.datamodels.find_one.return_value = None
        self.database.reports_overviews.find_one.return_value = None
        self.database.reports.count_documents.return_value = 0
        self.database.measurements.count_documents.return_value = 0
        self.mongo_client().quality_time_db = self.database

    def tearDown(self):
        bottle.app().uninstall(True)

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

    def test_update_database(self):
        """Test that some fields are removed."""
        self.database.reports.find.return_value = [
            dict(_id="report_uuid", subjects=dict(subject_uuid=dict(metrics=dict(metric_uuid=dict()))))]
        self.database.reports.count_documents.return_value = 1
        self.init_database("{}")
        self.database.reports.update_one.assert_called_once_with(
            {'_id': 'report_uuid'},
            update={
                '$unset': {
                    'summary': '',
                    'summary_by_subject': '',
                    'summary_by_tag': '',
                    'subjects.subject_uuid.metrics.metric_uuid.recent_measurements': '',
                    'subjects.subject_uuid.metrics.metric_uuid.status': '',
                    'subjects.subject_uuid.metrics.metric_uuid.value': ''}})
