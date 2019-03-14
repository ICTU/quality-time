"""Unit tests for the GitLab source."""

import unittest
from unittest.mock import Mock, patch

from collector.collector import collect_measurement


class GitLabTest(unittest.TestCase):
    """Unit tests for the GitLab metrics."""

    def setUp(self):
        """Test fixture."""
        self.mock_response = Mock()
        self.sources = dict(source_id=dict(type="gitlab", parameters=dict(url="http://gitlab/")))

    def test_nr_of_jobs(self):
        """Test that the number of jobs is returned."""
        self.mock_response.json.return_value = [dict(name="job", url="http://job")]
        metric = dict(type="jobs", sources=self.sources)
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(metric)
        self.assertEqual("1", response["sources"][0]["value"])

    def test_nr_of_failed_jobs(self):
        """Test that the number of failed jobs is returned."""
        self.mock_response.json.return_value = [dict(name="job", url="http://job", status="failed")]
        metric = dict(type="failed_jobs", sources=self.sources)
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(metric)
        self.assertEqual("1", response["sources"][0]["value"])
