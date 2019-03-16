"""Unit tests for the Jenkins source."""

import datetime
import unittest
from unittest.mock import Mock, patch

from collector.collector import collect_measurement


class JenkinsTestCase(unittest.TestCase):
    """Fixture for Jenkins unit tests."""

    def setUp(self):
        """Test fixture."""
        self.mock_response = Mock()
        self.sources = dict(source_id=dict(
            type="jenkins", parameters=dict(url="http://jenkins/")))


class JenkinsJobsTest(JenkinsTestCase):
    """Unit tests for the jobs metric."""

    def test_nr_of_jobs(self):
        """Test that the number of jobs is returned."""
        self.mock_response.json.return_value = dict(
            jobs=[dict(name="job", url="http://job", buildable=True)])
        metric = dict(type="jobs", sources=self.sources)
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(metric)
        self.assertEqual("1", response["sources"][0]["value"])

    def test_jobs(self):
        """Test that the jobs are returned."""
        self.mock_response.json.return_value = dict(jobs=[dict(name="job", url="http://job", buildable=True,
                                                               builds=[dict(timestamp=1540379612753)])])
        metric = dict(type="jobs", sources=self.sources)
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(metric)
        self.assertEqual([dict(datetime=datetime.datetime(2018, 10, 24, 11, 13, 32, 753000),
                               key="job", name="job", url="http://job")], response["sources"][0]["units"])


class JenkinsFailedJobsTest(JenkinsTestCase):
    """Unit tests for the failed jobs metric."""

    def test_nr_of_failed_jobs(self):
        """Test that the number of failed jobs is returned."""
        self.mock_response.json.return_value = dict(
            jobs=[dict(name="job", url="http://job", buildable=True, color="red")])
        metric = dict(type="failed_jobs", sources=self.sources)
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(metric)
        self.assertEqual("1", response["sources"][0]["value"])

    def test_failed_jobs(self):
        """Test that the failed jobs are returned."""
        self.mock_response.json.return_value = dict(
            jobs=[dict(name="job", url="http://job", buildable=True, color="red")])
        metric = dict(type="failed_jobs", sources=self.sources)
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(metric)
        self.assertEqual(
            [dict(datetime=None, key="job", name="job", url="http://job")], response["sources"][0]["units"])


class JenkinsUnusedJobsTest(JenkinsTestCase):
    """Unit tests for the unused jobs metric."""

    def test_unused_jobs(self):
        """Test that the number of unused jobs is returned."""
        self.mock_response.json.return_value = dict(
            jobs=[dict(
                name="job", url="http://job", buildable=True, color="red", builds=[dict(timestamp="1548311610349")])])
        metric = dict(type="unused_jobs", sources=self.sources)
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(metric)
        self.assertEqual("1", response["sources"][0]["value"])

    def test_unbuild_job(self):
        """Test that jobs without builds are ignored."""
        self.mock_response.json.return_value = dict(
            jobs=[dict(name="job", url="http://job", buildable=True, color="red")])
        metric = dict(type="unused_jobs", sources=self.sources)
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(metric)
        self.assertEqual("0", response["sources"][0]["value"])
