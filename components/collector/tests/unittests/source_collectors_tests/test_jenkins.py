"""Unit tests for the Jenkins source."""

from datetime import datetime
from unittest.mock import Mock, patch

from .source_collector_test_case import SourceCollectorTestCase


class JenkinsTestCase(SourceCollectorTestCase):
    """Fixture for Jenkins unit tests."""

    sources = dict(source_id=dict(type="jenkins", parameters=dict(url="http://jenkins/", failure_type=["Red"])))

    def collect(self, metric, jenkins_json=None):
        jenkins_response = Mock()
        jenkins_response.json.return_value = jenkins_json
        with patch("requests.get", return_value=jenkins_response):
            return super().collect(metric)


class JenkinsFailedJobsTest(JenkinsTestCase):
    """Unit tests for the failed jobs metric."""

    metric = dict(type="failed_jobs", sources=JenkinsTestCase.sources, addition="sum")

    def test_nr_of_failed_jobs(self):
        """Test that the number of failed jobs is returned."""
        jenkins_json = dict(
            jobs=[dict(name="job", url="http://job", buildable=True, color="red", builds=[dict(result="red")],
                       jobs=[dict(name="child_job", url="http://child_job", buildable=True, color="red",
                                  builds=[dict(result="red")])])])
        response = self.collect(self.metric, jenkins_json)
        self.assert_value("2", response)

    def test_failed_jobs(self):
        """Test that the failed jobs are returned."""
        jenkins_json = dict(
            jobs=[dict(name="job", url="http://job", buildable=True, color="red",
                       builds=[dict(result="red", timestamp="1552686540953")])])
        response = self.collect(self.metric, jenkins_json)
        build_age = str((datetime.now() - datetime.utcfromtimestamp(1552686540953 / 1000.)).days)
        self.assert_entities(
            [dict(build_date="2019-03-15", build_age=build_age, build_status="Red",
                  key="job", name="job", url="http://job")], response)

    def test_no_builds(self):
        """Test no builds."""
        jenkins_json = dict(jobs=[dict(name="job", url="http://job", buildable=True, color="notbuilt", builds=[])])
        response = self.collect(self.metric, jenkins_json)
        self.assert_entities([], response)


class JenkinsUnusedJobsTest(JenkinsTestCase):
    """Unit tests for the unused jobs metric."""

    metric = dict(type="unused_jobs", sources=JenkinsTestCase.sources, addition="sum")

    def test_unused_jobs(self):
        """Test that the number of unused jobs is returned."""
        jenkins_json = dict(
            jobs=[dict(
                name="job", url="http://job", buildable=True, color="red", builds=[dict(timestamp="1548311610349")])])
        response = self.collect(self.metric, jenkins_json)
        self.assert_value("1", response)

    def test_unbuild_job(self):
        """Test that jobs without builds are ignored."""
        jenkins_json = dict(
            jobs=[dict(name="job", url="http://job", buildable=True, color="red")])
        response = self.collect(self.metric, jenkins_json)
        self.assert_value("0", response)
