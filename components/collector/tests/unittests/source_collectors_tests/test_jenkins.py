"""Unit tests for the Jenkins source."""

from datetime import datetime

from .source_collector_test_case import SourceCollectorTestCase


class JenkinsTestCase(SourceCollectorTestCase):
    """Fixture for Jenkins unit tests."""

    def setUp(self):
        super().setUp()
        self.sources = dict(
            source_id=dict(type="jenkins", parameters=dict(url="https://jenkins/", failure_type=["Red"])))


class JenkinsFailedJobsTest(JenkinsTestCase):
    """Unit tests for the failed jobs metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="failed_jobs", sources=self.sources, addition="sum")

    def test_nr_of_failed_jobs(self):
        """Test that the number of failed jobs is returned."""
        jenkins_json = dict(
            jobs=[
                dict(
                    name="job", url="https://job", buildable=True, color="red",
                    builds=[dict(result="red", timestamp="1552686540953")],
                    jobs=[
                        dict(
                            name="child_job", url="https://child_job", buildable=True, color="red",
                            builds=[dict(result="red", timestamp="1552686540953")])])])
        response = self.collect(self.metric, get_request_json_return_value=jenkins_json)
        self.assert_measurement(response, value="2")

    def test_failed_jobs(self):
        """Test that the failed jobs are returned."""
        jenkins_json = dict(
            jobs=[dict(name="job", url="https://job", buildable=True, color="red",
                       builds=[dict(result="red", timestamp="1552686540953")])])
        response = self.collect(self.metric, get_request_json_return_value=jenkins_json)
        age = str((datetime.now() - datetime.utcfromtimestamp(1552686540953 / 1000.)).days)
        expected_entities = [
            dict(build_date="2019-03-15", build_age=age, build_status="Red", key="job", name="job", url="https://job")]
        self.assert_measurement(response, entities=expected_entities)

    def test_no_builds(self):
        """Test no builds."""
        jenkins_json = dict(jobs=[dict(name="job", url="https://job", buildable=True, color="notbuilt", builds=[])])
        response = self.collect(self.metric, get_request_json_return_value=jenkins_json)
        self.assert_measurement(response, entities=[])


class JenkinsUnusedJobsTest(JenkinsTestCase):
    """Unit tests for the unused jobs metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="unused_jobs", sources=self.sources, addition="sum")

    def test_unused_jobs(self):
        """Test that the number of unused jobs is returned."""
        jenkins_json = dict(
            jobs=[dict(
                name="job", url="https://job", buildable=True, color="red", builds=[dict(timestamp="1548311610349")])])
        response = self.collect(self.metric, get_request_json_return_value=jenkins_json)
        self.assert_measurement(response, value="1")

    def test_unbuild_job(self):
        """Test that jobs without builds are ignored."""
        jenkins_json = dict(jobs=[dict(name="job", url="https://job", buildable=True, color="red")])
        response = self.collect(self.metric, get_request_json_return_value=jenkins_json)
        self.assert_measurement(response, value="0")
