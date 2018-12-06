import unittest
from unittest.mock import patch, Mock
import requests

from quality_time.source import Source


class SourceTest(unittest.TestCase):
    """Unit tests for the source class."""

    @patch("requests.get")
    def setUp(self, mock_get):
        """Simple response fixture."""
        mock_response = Mock()
        mock_response.text = "2"
        mock_get.return_value = mock_response
        self.response = Source.get("metric", ["http://url"], [])

    def test_source_name(self):
        """Test that the source name is returned."""
        self.assertEqual("Source", self.response["source"])
        
    def test_metric_name(self):
        """Test that the metric name is returned."""
        self.assertEqual("metric", self.response["metric"])

    def test_source_metric_name(self):
        """Test that the metric name as used in the source is returned."""
        self.assertEqual("metric", self.response["source_metric"])

    def test_source_response_url(self):
        """Test that the url used for contacting the source is returned."""
        self.assertEqual("http://url", self.response["source_responses"][0]["url"])

    def test_source_response_component(self):
        """Test that the component used for contacting the source is returned."""
        self.assertEqual(None, self.response["source_responses"][0]["component"])

    def test_source_response_api_url(self):
        """Test that the api url used for contacting the source is returned."""
        self.assertEqual("http://url", self.response["source_responses"][0]["api_url"])

    def test_source_response_landing_url(self):
        """Test that the landing url for the source is returned."""
        self.assertEqual("http://url", self.response["source_responses"][0]["landing_url"])

    def test_source_response_measurement(self):
        """Test that the measurement for the source is returned."""
        self.assertEqual("2", self.response["source_responses"][0]["measurement"])

    def test_calculated_measurement(self):
        """Test that the calculated measurement is returned."""
        self.assertEqual("2", self.response["measurement"])


class SourceWithComponentTest(unittest.TestCase):
    """Unit tests for the source class with a component."""

    def setUp(self):
        """Simple response fixture."""
        self.response = Source.get("metric", ["http://url"], ["component id"])

    def test_source_response_component(self):
        """Test that the component used for contacting the source is returned."""
        self.assertEqual("component id", self.response["source_responses"][0]["component"])


class SourceWithMultipleURLsTest(unittest.TestCase):
    """Unit tests for the source class with multiple URLs."""

    @patch("requests.get")
    def setUp(self, mock_get):
        """Simple response fixture."""
        mock_response = Mock()
        mock_response.text = "2"
        mock_get.return_value = mock_response
        self.response = Source.get("metric", ["http://url1", "http://url2"], [])

    def test_source_response_component(self):
        """Test that the component used for contacting the source is returned."""
        self.assertEqual(None, self.response["source_responses"][1]["component"])

    def test_calculated_measurement(self):
        """Test that the calculated measurement is returned."""
        self.assertEqual("4", self.response["measurement"])


class SourceWithMultipleURLsAndComponentsTest(unittest.TestCase):
    """Unit tests for the source class with multiple URLs and components."""

    @patch("requests.get")
    def setUp(self, mock_get):
        """Simple response fixture."""
        mock_response = Mock()
        mock_response.text = "2"
        mock_get.return_value = mock_response
        self.response = Source.get("metric", ["http://url1", "http://url2"], ["component id 1", "component id 2"])

    def test_source_response_component(self):
        """Test that the components used for contacting the source is returned."""
        self.assertEqual("component id 2", self.response["source_responses"][1]["component"])

    def test_calculated_measurement(self):
        """Test that the calculated measurement is returned."""
        self.assertEqual("4", self.response["measurement"])
