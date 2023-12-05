"""Unit tests for the search endpoint."""

from unittest.mock import Mock, patch

from routes import search

from tests.base import DatabaseTestCase, disable_logging
from tests.fixtures import METRIC_ID, METRIC_ID2, REPORT_ID, REPORT_ID2, SOURCE_ID, SOURCE_ID2, SUBJECT_ID, SUBJECT_ID2


class SearchTest(DatabaseTestCase):
    """Unit tests for searching domain objects."""

    @patch("bottle.request", Mock(json={"attribute_name": "attribute_value"}))
    def test_no_reports(self):
        """Test that no domain objects can be found if there are no reports."""
        self.database.reports.find.return_value = []
        for domain_object_type in ("metric", "report", "source", "subject"):
            expected_results = {
                "domain_object_type": domain_object_type,
                "ok": True,
                "search_query": {"attribute_name": "attribute_value"},
                "uuids": [],
            }
            self.assertEqual(expected_results, search(domain_object_type, self.database))

    @patch("bottle.request", Mock(json={"title": "Report 1"}))
    def test_search_report(self):
        """Test that a report can be found."""
        self.database.reports.find.return_value = [
            {"title": "Report 1", "report_uuid": REPORT_ID},
            {"title": "Report 2", "report_uuid": REPORT_ID2},
        ]
        expected_results = {
            "domain_object_type": "report",
            "ok": True,
            "search_query": {"title": "Report 1"},
            "uuids": [REPORT_ID],
        }
        self.assertEqual(expected_results, search("report", self.database))

    @patch("bottle.request", Mock(json={"name": "Subject 1"}))
    def test_search_subject(self):
        """Test that a subject can be found."""
        self.database.reports.find.return_value = [
            {"subjects": {SUBJECT_ID: {"name": "Subject 1"}}},
            {"subjects": {SUBJECT_ID2: {"name": "Subject 2"}}},
        ]
        expected_results = {
            "domain_object_type": "subject",
            "ok": True,
            "search_query": {"name": "Subject 1"},
            "uuids": [SUBJECT_ID],
        }
        self.assertEqual(expected_results, search("subject", self.database))

    @patch("bottle.request", Mock(json={"name": "Metric 1"}))
    def test_search_metric(self):
        """Test that a metric can be found."""
        self.database.reports.find.return_value = [
            {"subjects": {SUBJECT_ID: {"metrics": {METRIC_ID: {"name": "Metric 1"}}}}},
            {"subjects": {SUBJECT_ID2: {"metrics": {METRIC_ID2: {"name": "Metric 2"}}}}},
        ]
        expected_results = {
            "domain_object_type": "metric",
            "ok": True,
            "search_query": {"name": "Metric 1"},
            "uuids": [METRIC_ID],
        }
        self.assertEqual(expected_results, search("metric", self.database))

    @patch("bottle.request", Mock(json={"name": "Metric"}))
    def test_search_metric_multiple_matches(self):
        """Test that multiple metrics can be found."""
        self.database.reports.find.return_value = [
            {"subjects": {SUBJECT_ID: {"metrics": {METRIC_ID: {"name": "Metric"}}}}},
            {"subjects": {SUBJECT_ID2: {"metrics": {METRIC_ID2: {"name": "Metric"}}}}},
        ]
        expected_results = {
            "domain_object_type": "metric",
            "ok": True,
            "search_query": {"name": "Metric"},
            "uuids": [METRIC_ID, METRIC_ID2],
        }
        self.assertEqual(expected_results, search("metric", self.database))

    @patch("bottle.request", Mock(json={"name": "Source 1"}))
    def test_search_source(self):
        """Test that a source can be found."""
        self.database.reports.find.return_value = [
            {
                "subjects": {
                    SUBJECT_ID: {
                        "metrics": {METRIC_ID: {"sources": {SOURCE_ID: {"name": "Source 1", "parameters": {}}}}}
                    }
                }
            },
            {
                "subjects": {
                    SUBJECT_ID2: {
                        "metrics": {METRIC_ID2: {"sources": {SOURCE_ID2: {"name": "Source 2", "parameters": {}}}}}
                    }
                }
            },
        ]
        expected_results = {
            "domain_object_type": "source",
            "ok": True,
            "search_query": {"name": "Source 1"},
            "uuids": [SOURCE_ID],
        }
        self.assertEqual(expected_results, search("source", self.database))

    @patch("bottle.request", Mock(json={"url": "https://example.org"}))
    def test_search_source_by_parameter(self):
        """Test that a source can be found by parameter."""
        self.database.reports.find.return_value = [
            {
                "subjects": {
                    SUBJECT_ID: {
                        "metrics": {METRIC_ID: {"sources": {SOURCE_ID: {"parameters": {"url": "https://example.org"}}}}}
                    }
                }
            },
            {
                "subjects": {
                    SUBJECT_ID2: {
                        "metrics": {
                            METRIC_ID2: {"sources": {SOURCE_ID2: {"parameters": {"url": "https://example2.org"}}}}
                        }
                    }
                }
            },
        ]
        expected_results = {
            "domain_object_type": "source",
            "ok": True,
            "search_query": {"url": "https://example.org"},
            "uuids": [SOURCE_ID],
        }
        self.assertEqual(expected_results, search("source", self.database))

    @disable_logging
    @patch("bottle.request", Mock(json={"name": "Source"}))
    def test_failed_search(self):
        """Test that an error response is returned when an exception occurs during the search."""
        self.database.reports.find.side_effect = [RuntimeError("error message")]
        expected_results = {
            "domain_object_type": "source",
            "error": "error message",
            "ok": False,
            "search_query": {"name": "Source"},
        }
        self.assertEqual(expected_results, search("source", self.database))

    @disable_logging
    @patch("bottle.request", Mock(json={}))
    def test_failed_parsing_of_search_query(self):
        """Test that an error response is returned when the search query could not be parsed."""
        expected_results = {"domain_object_type": "source", "error": "'pop from an empty set'", "ok": False}
        self.assertEqual(expected_results, search("source", self.database))
