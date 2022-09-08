"""Unit tests for the report initialization functions."""

import json
import pathlib
from unittest.mock import Mock, mock_open, patch

from shared.initialization.report import import_example_reports, import_report

from ..base import DataModelTestCase


class ReportInitTest(DataModelTestCase):
    """Unit tests for the report import code."""

    def setUp(self) -> None:
        """Override to create database and JSON fixtures."""
        self.database = Mock()
        self.database.reports.distinct.return_value = []
        self.database.datamodels.find_one.return_value = self.DATA_MODEL
        self.report_json = json.dumps(
            dict(
                report_uuid="id",
                subjects=[
                    dict(
                        name="name",
                        type="software",
                        metrics=[
                            dict(type="security_warnings", sources=[dict(type="sonarqube", parameters=dict(url={}))])
                        ],
                    )
                ],
            )
        )
        self.database.sessions.find_one.return_value = dict(user="jadoe")

    def import_report(self, report_json: str) -> None:
        """Import the report."""
        with patch.object(pathlib.Path, "open", mock_open(read_data=report_json)):
            import_report(self.database, pathlib.Path("filename"))

    def test_import(self):
        """Test that a report can be imported."""
        self.import_report(self.report_json)
        self.database.reports.insert_one.assert_called_once()

    def test_import_is_skipped(self):
        """Test that a report isn't imported when it's already in the database."""
        self.database.reports.distinct.return_value = ["id"]
        self.import_report(self.report_json)
        self.database.reports.insert_one.assert_not_called()

    def test_import_example_report(self):
        """Test that the example reports are imported."""
        with patch.object(pathlib.Path, "glob", Mock(return_value=[pathlib.Path("example-report.json")])), patch.object(
            pathlib.Path, "open", mock_open(read_data=self.report_json)
        ):
            import_example_reports(self.database)
        self.database.reports.insert_one.assert_called_once()
