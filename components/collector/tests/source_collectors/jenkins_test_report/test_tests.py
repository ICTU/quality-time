"""Unit tests for the Jenkins test report tests collector."""

from .base import JenkinsTestReportTestCase


class JenkinsTestReportTestsTest(JenkinsTestReportTestCase):
    """Unit tests for the Jenkins test report tests collector."""

    METRIC_TYPE = "tests"

    async def test_nr_of_tests(self):
        """Test that the number of tests is returned."""
        jenkins_json = dict(
            failCount=1,
            passCount=1,
            suites=[
                dict(
                    cases=[
                        dict(status="FAILED", name="tc1", className="c1", age=1),
                        dict(status="PASSED", name="tc2", className="c2", age=0),
                    ]
                )
            ],
        )
        response = await self.collect(self.metric, get_request_json_return_value=jenkins_json)
        self.assert_measurement(
            response,
            value="2",
            total="2",
            entities=[
                dict(class_name="c1", key="tc1", name="tc1", test_result="failed", age="1"),
                dict(class_name="c2", key="tc2", name="tc2", test_result="passed", age="0"),
            ],
        )

    async def test_nr_of_tests_with_aggregated_report(self):
        """Test that the number of tests is returned when the test report is an aggregated report."""
        jenkins_json = dict(
            childReports=[
                dict(
                    result=dict(
                        failCount=1,
                        passCount=1,
                        suites=[
                            dict(
                                cases=[
                                    dict(status="FAILED", name="tc1", className="c1", age=2),
                                    dict(status="PASSED", name="tc2", className="c2", age=0),
                                ]
                            )
                        ],
                    )
                )
            ]
        )
        response = await self.collect(self.metric, get_request_json_return_value=jenkins_json)
        self.assert_measurement(
            response,
            value="2",
            total="2",
            entities=[
                dict(class_name="c1", key="tc1", name="tc1", test_result="failed", age="2"),
                dict(class_name="c2", key="tc2", name="tc2", test_result="passed", age="0"),
            ],
        )

    async def test_nr_of_passed_tests(self):
        """Test that the number of passed tests is returned."""
        jenkins_json = dict(
            failCount=1,
            passCount=1,
            suites=[
                dict(
                    cases=[
                        dict(status="FAILED", name="tc1", className="c1", age=3),
                        dict(status="PASSED", name="tc2", className="c2", age=0),
                    ]
                )
            ],
        )
        self.sources["source_id"]["parameters"]["test_result"] = ["passed"]
        response = await self.collect(self.metric, get_request_json_return_value=jenkins_json)
        expected_entities = [dict(class_name="c2", key="tc2", name="tc2", test_result="passed", age="0")]
        self.assert_measurement(response, value="1", total="2", entities=expected_entities)

    async def test_nr_of_failed_tests(self):
        """Test that the number of failed tests is returned."""
        jenkins_json = dict(
            failCount=2,
            passCount=1,
            suites=[
                dict(
                    cases=[
                        dict(status="FAILED", name="tc1", className="c1", age=1),
                        dict(status="FAILED", name="tc2", className="c2", age=2),
                        dict(status="PASSED", name="tc3", className="c3", age=0),
                    ]
                )
            ],
        )
        self.sources["source_id"]["parameters"]["test_result"] = ["failed"]
        response = await self.collect(self.metric, get_request_json_return_value=jenkins_json)
        expected_entities = [
            dict(class_name="c1", key="tc1", name="tc1", test_result="failed", age="1"),
            dict(class_name="c2", key="tc2", name="tc2", test_result="failed", age="2"),
        ]
        self.assert_measurement(response, value="2", total="3", entities=expected_entities)
