"""Unit tests for the Jenkins test report source."""

from datetime import datetime

from collector_utilities.functions import days_ago
from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class JenkinsTestReportTest(SourceCollectorTestCase):
    """Unit tests for the Jenkins test report metrics."""

    def setUp(self):
        super().setUp()
        self.sources = dict(source_id=dict(type="jenkins_test_report", parameters=dict(url="https://jenkins/job")))

    async def test_nr_of_tests(self):
        """Test that the number of tests is returned."""
        jenkins_json = dict(
            failCount=1, passCount=1, suites=[dict(
                cases=[dict(status="FAILED", name="tc1", className="c1"),
                       dict(status="PASSED", name="tc2", className="c2")])])
        metric = dict(type="tests", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=jenkins_json)
        self.assert_measurement(
            response, value="2",
            entities=[
                dict(class_name="c1", key="tc1", name="tc1", test_result="failed"),
                dict(class_name="c2", key="tc2", name="tc2", test_result="passed")])

    async def test_nr_of_tests_with_aggregated_report(self):
        """Test that the number of tests is returned when the test report is an aggregated report."""
        jenkins_json = dict(
            childReports=[
                dict(
                    result=dict(
                        failCount=1, passCount=1,
                        suites=[dict(
                            cases=[
                                dict(status="FAILED", name="tc1", className="c1"),
                                dict(status="PASSED", name="tc2", className="c2")])]))])
        metric = dict(type="tests", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=jenkins_json)
        self.assert_measurement(
            response, value="2",
            entities=[
                dict(class_name="c1", key="tc1", name="tc1", test_result="failed"),
                dict(class_name="c2", key="tc2", name="tc2", test_result="passed")])

    async def test_nr_of_passed_tests(self):
        """Test that the number of passed tests is returned."""
        jenkins_json = dict(
            failCount=1, passCount=1, suites=[dict(
                cases=[dict(status="FAILED", name="tc1", className="c1"),
                       dict(status="PASSED", name="tc2", className="c2")])])
        self.sources["source_id"]["parameters"]["test_result"] = ["passed"]
        metric = dict(type="tests", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=jenkins_json)
        expected_entities = [dict(class_name="c2", key="tc2", name="tc2", test_result="passed")]
        self.assert_measurement(response, value="1", entities=expected_entities)

    async def test_nr_of_failed_tests(self):
        """Test that the number of failed tests is returned."""
        jenkins_json = dict(
            failCount=2, suites=[dict(
                cases=[dict(status="FAILED", name="tc1", className="c1"),
                       dict(status="FAILED", name="tc2", className="c2"),
                       dict(status="PASSED", name="tc3", className="c3")])])
        self.sources["source_id"]["parameters"]["test_result"] = ["failed"]
        metric = dict(type="tests", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_json_return_value=jenkins_json)
        expected_entities = [
            dict(class_name="c1", key="tc1", name="tc1", test_result="failed"),
            dict(class_name="c2", key="tc2", name="tc2", test_result="failed")]
        self.assert_measurement(response, value="2", entities=expected_entities)

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        metric = dict(type="source_up_to_dateness", addition="max", sources=self.sources)
        response = await self.collect(
            metric, get_request_json_return_value=dict(suites=[dict(timestamp="2019-04-02T08:52:50")]))
        expected_age = (datetime.now() - datetime(2019, 4, 2, 8, 52, 50)).days
        self.assert_measurement(response, value=str(expected_age))

    async def test_source_up_to_dateness_without_timestamps(self):
        """Test that the job age in days is returned if the test report doesn't contain timestamps."""
        metric = dict(type="source_up_to_dateness", addition="max", sources=self.sources)
        response = await self.collect(
            metric,
            get_request_json_side_effect=[dict(suites=[dict(timestamp=None)]), dict(timestamp="1565284457173")])
        expected_age = days_ago(datetime.fromtimestamp(1565284457173 / 1000.))
        self.assert_measurement(response, value=str(expected_age))
