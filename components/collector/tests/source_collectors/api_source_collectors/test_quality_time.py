"""Unit tests for the Quality-time source collector(s)."""

from datetime import datetime

from dateutil.parser import parse

from collector_utilities.functions import days_ago
from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class QualityTimeMetricsTest(SourceCollectorTestCase):
    """Fixture for Quality-time metrics unit tests."""

    def setUp(self):
        super().setUp()
        self.url = "https://quality-time"
        self.api_url = f"{self.url}/api/v3/reports"
        self.sources = dict(
            source_id=dict(
                type="quality_time",
                parameters=dict(
                    url=self.url, reports=["r1"], status=["target not met (red)"], tags=["security"],
                    metric_type=["tests", "violations"], source_type=["sonarqube"])))
        self.reports = dict(
            reports=[
                dict(
                    title="R1", report_uuid="r1",
                    subjects=dict(
                        s1=dict(
                            name="S1",
                            metrics=dict(
                                m1=dict(
                                    tags=["security"], scale="count", type="violations", target="1",
                                    sources=dict(s1=dict(type="sonarqube")), recent_measurements=[
                                        dict(count=dict(status="target_not_met", value="10"),
                                             end="2020-06-23T07:53:17+00:00"),
                                        dict(count=dict(status="target_met", value="0"),
                                             end="2020-06-24T07:53:17+00:00")
                                    ]),
                                m2=dict(
                                    tags=["security"], scale="count", type="violations", target="2",
                                    sources=dict(s2=dict(type="sonarqube")), recent_measurements=[
                                        dict(count=dict(status="target_not_met", value="20"),
                                             end="2020-06-25T07:53:17+00:00")
                                    ]),
                                m3=dict(
                                    tags=["security"], scale="count", type="violations", target="3",
                                    recent_measurements=[], sources=dict(s3=dict(type="sonarqube"))),
                                m4=dict(
                                    tags=["security"], scale="count", type="violations", target="4",
                                    sources=dict(s4=dict(type="junit"))),
                                m5=dict(
                                    tags=["performance"], scale="count", type="violations", target="5",
                                    sources=dict(s5=dict(type="sonarqube"))),
                                m6=dict(
                                    tags=["security"], scale="count", type="loc", target="6",
                                    sources=dict(s6=dict(type="sonarqube"))))))),
                dict(
                    title="R2", report_uuid="r2")])

    async def test_nr_of_metrics(self):
        """Test that the number of metrics is returned."""
        metric = dict(type="metrics", sources=self.sources, addition="sum")
        response = await self.collect(metric, get_request_json_return_value=self.reports)
        # The count should be one because the user selected metrics from report "r1", with status "target_not_met",
        # metric type "tests" or "violations", source type "sonarqube" or "junit", and tag "security".
        # Only m2 matches those criteria.
        self.assert_measurement(
            response, value="1", total="3", api_url=self.api_url, landing_url=self.url,
            entities=[
                dict(
                    key="m2", report="R1", subject="S1", metric="Violations", report_url=f"{self.url}/r1",
                    subject_url=f"{self.url}/r1#s1", metric_url=f"{self.url}/r1#m2", measurement="20 violations",
                    target="≦ 2 violations", status="target_not_met")])

    async def test_nr_of_metrics_without_reports(self):
        """Test that the number of metrics is returned."""
        self.sources["source_id"]["parameters"]["reports"] = []
        metric = dict(type="metrics", sources=self.sources, addition="sum")
        response = await self.collect(metric, get_request_json_return_value=dict(reports=[]))
        self.assert_measurement(
            response, value=None, total=None, api_url=self.api_url, parse_error="No reports found",
            landing_url=self.url, entities=[])

    async def test_nr_of_metrics_without_correct_report(self):
        """Test that the number of metrics is returned."""
        self.reports["reports"].pop(0)
        metric = dict(type="metrics", sources=self.sources, addition="sum")
        response = await self.collect(metric, get_request_json_return_value=self.reports)
        self.assert_measurement(
            response, value=None, total=None, api_url=self.api_url, parse_error="No reports found with title or id",
            landing_url=self.url, entities=[])

    async def test_source_up_to_dateness(self):
        """Test that the source up-to-dateness of all reports can be measured."""
        self.sources["source_id"]["parameters"]["reports"] = []
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="sum")
        response = await self.collect(metric, get_request_json_return_value=self.reports)
        expected_age = days_ago(parse("2020-06-24T07:53:17+00:00"))
        self.assert_measurement(
            response, value=str(expected_age), total="100", api_url=self.api_url, landing_url=self.url, entities=[])

    async def test_source_up_to_dateness_report(self):
        """Test that the source up-to-dateness of a specific report can be measured."""
        self.sources["source_id"]["parameters"]["reports"] = ["r2"]
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="sum")
        response = await self.collect(metric, get_request_json_return_value=self.reports)
        expected_age = days_ago(datetime.min)
        self.assert_measurement(
            response, value=str(expected_age), total="100", api_url=self.api_url, landing_url=self.url, entities=[])
