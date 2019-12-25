"""Unit tests for the report initialization functions."""

import json
import unittest
import pathlib
from unittest.mock import Mock, mock_open, patch

from src.initialization.report import import_report, import_example_reports


class ReportInitTest(unittest.TestCase):
    """Unit tests for the report import code."""

    def setUp(self) -> None:
        self.database = Mock()

    def import_report(self, report_json: str) -> None:
        """Import the report."""
        with patch.object(pathlib.Path, "open", mock_open(read_data=report_json)):
            import_report(self.database, pathlib.Path("filename"))

    def test_import(self):
        """Test that a report can be imported."""
        self.database.reports.find_one.return_value = None
        self.database.datamodels.find_one.return_value = dict(
            _id="id",
            subjects=dict(subject_type=dict(name="name", description="")),
            metrics=dict(
                metric_type=dict(default_scale="count", addition="sum", target="0", near_target="0", tags=[])),
            sources=dict(
                source_type=dict(
                    parameters=dict(
                        p1=dict(default_value="p1", metrics=["metric_type"]),
                        p2=dict(default_value="p2", metrics=["metric_type"])))))
        report_json = json.dumps(
            dict(
                report_uuid="id",
                subjects=[dict(name="name", type="subject_type", metrics=[
                    dict(type="metric_type", sources=[
                        dict(type="source_type", parameters=dict(p1=dict()))
                    ])
                ])]))
        self.import_report(report_json)
        self.database.reports.insert.assert_called_once()

    def test_import_is_skipped(self):
        """Test that a report isn't imported when it's already in the database."""
        self.database.reports.find_one.return_value = True
        self.import_report('{"report_uuid": "id", "subjects": []}')
        self.database.reports.insert.assert_not_called()

    def test_import_example_report(self):
        """Test that the example reports are imported."""
        mock_glob = Mock(return_value=["filename"])
        with patch("glob.glob", mock_glob):
            with patch("builtins.open", mock_open(read_data='{"report_uuid": "id", "subjects": []}')):
                import_example_reports(self.database)
        self.database.reports.insert.assert_not_called()
