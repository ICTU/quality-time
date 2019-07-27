"""Unit tests for the Jenkins test report source."""

from datetime import datetime

from .source_collector_test_case import SourceCollectorTestCase


class JenkinsTestReportTest(SourceCollectorTestCase):
    """Unit tests for the Jenkins test report metrics."""

    def setUp(self):
        super().setUp()
        self.sources = dict(source_id=dict(type="jenkins_test_report", parameters=dict(url="http://jenkins/job")))

    def test_nr_of_tests(self):
        """Test that the number of tests is returned."""
        metric = dict(type="tests", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=dict(passCount=4, failCount=2))
        self.assert_value("6", response)

    def test_nr_of_failed_tests(self):
        """Test that the number of failed tests is returned."""
        jenkins_json = dict(
            failCount=2, suites=[dict(
                cases=[dict(status="FAILED", name="tc1", className="c1"),
                       dict(status="FAILED", name="tc2", className="c2")])])
        metric = dict(type="failed_tests", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_json_return_value=jenkins_json)
        self.assert_value("2", response)
        self.assert_entities(
            [dict(class_name="c1", key="tc1", name="tc1", failure_type="failed"),
             dict(class_name="c2", key="tc2", name="tc2", failure_type="failed")],
            response)

    def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        metric = dict(type="source_up_to_dateness", addition="max", sources=self.sources)
        response = self.collect(
            metric, get_request_json_return_value=dict(suites=[dict(timestamp="2019-04-02T08:52:50")]))
        expected_age = (datetime.now() - datetime(2019, 4, 2, 8, 52, 50)).days
        self.assert_value(str(expected_age), response)
