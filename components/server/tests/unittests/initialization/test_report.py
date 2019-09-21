"""Unit tests for the report initialization functions."""

import json
import unittest
from unittest.mock import Mock, mock_open, patch

from src.initialization.report import import_report, import_example_reports


class ReportInitTest(unittest.TestCase):
    """Unit tests for the report import code."""

    def test_import(self):
        """Test that a report can be imported."""
        database = Mock()
        database.reports.find_one.return_value = None
        database.datamodels.find_one.return_value = dict(
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
        with patch("builtins.open", mock_open(read_data=report_json)):
            import_report(database, "filename")
        database.reports.insert.assert_called_once()

    def test_import_is_skipped(self):
        """Test that a report isn't imported when it's already in the database."""
        database = Mock()
        database.reports.find_one.return_value = True
        with patch("builtins.open", mock_open(read_data='{"report_uuid": "id", "subjects": []}')):
            import_report(database, "filename")
        database.reports.insert.assert_not_called()


class ExampleReportInitTest(unittest.TestCase):
    """Unit tests for the example report import code."""

    def test_import(self):
        """Test that the example reports are imported."""
        database = Mock()
        database.reports.find_one.return_value = True
        mock_glob = Mock(return_value=["filename"])
        with patch("glob.glob", mock_glob):
            with patch("builtins.open", mock_open(read_data='{"report_uuid": "id", "subjects": []}')):
                import_example_reports(database)
        database.reports.insert.assert_not_called()
