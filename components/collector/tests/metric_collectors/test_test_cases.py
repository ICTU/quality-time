"""Unit tests for the test cases metric collector."""

import unittest
from unittest.mock import AsyncMock, patch

from base_collectors.metric_collector import MetricCollector
from model import MetricMeasurement
from source_collectors.jira.issues import JiraIssues


class TestCasesTest(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the test cases metric collector."""

    TESTNG_XML = """
        <testng-results skipped="0" failed="1" ignored="1" total="2" passed="1">
          <suite name="suite1">
            <test name="test1">
              <class name="class">
                <test-method status="PASS" name="method1" is-config="true" />
                <test-method status="PASS" name="method2" description="key-1" />
                <test-method status="FAIL" name="method3, key-1" />
                <test-method status="FAIL" name="method4" description="no_such_key-1" />
              </class>
            </test>
          </suite>
        </testng-results>
        """
    JUNIT_XML = """
        <testsuite tests="3" errors="0" failures="2" skipped="0">
            <testcase name="key-1; step 1"/>
            <testcase name="key-1; step 2"><failure /></testcase>
            <testcase name="no_such_key-1"><failure /></testcase>
        </testsuite>
        """
    ROBOT_FRAMEWORK_XML_V4 = """<?xml version="1.0" encoding="UTF-8"?>
        <robot generator="Robot 4.0b3.dev1 (Python 3.9.1 on linux)" generated="20210212 17:27:03.027">
            <suite>
                <test id="s1-t1" name="key-1; Test 1">
                    <status status="PASS"></status>
                </test>
                <test id="s1-t2" name="key-1; Test 2">
                    <status status="FAIL"></status>
                </test>
            </suite>
            <statistics>
                <total>
                    <stat pass="1" fail="1" skip="0">All Tests</stat>
                </total>
            </statistics>
        </robot>"""
    CREATED = "2020-08-06T16:36:48.000+0200"

    def setUp(self) -> None:
        """Extend to set up test fixtures."""
        super().setUp()
        self.session = AsyncMock()
        self.response = self.session.get.return_value = AsyncMock()
        self.test_cases_json = {"total": 2, "issues": [self.jira_issue(), self.jira_issue("key-2")]}
        self.response.json = AsyncMock(side_effect=[[], self.test_cases_json, self.test_cases_json])
        self.jira_url = "https://jira"
        self.test_report_url = "https://report_xml"

    def jira_issue(self, key: str = "key-1", **fields):
        """Create a Jira issue."""
        return {"id": key, "key": key, "fields": dict(created=self.CREATED, summary=f"Summary {key}", **fields)}

    def jira_entity(self, key: str = "key-1", test_result: str = "untested"):
        """Create an entity."""
        return {
            "key": key,
            "issue_key": key,
            "summary": f"Summary {key}",
            "url": f"{self.jira_url}/browse/{key}",
            "created": self.CREATED,
            "updated": None,
            "status": None,
            "priority": None,
            "type": "Unknown issue type",
            "test_result": test_result,
        }

    async def collect(self, sources) -> MetricMeasurement | None:
        """Collect the measurement."""
        metric = {"type": "test_cases", "sources": sources}
        # Instead of instantiating the TestCases collector directly, we look up the collector by the metric type
        # to get full coverage:
        test_cases_collector_class = MetricCollector.get_subclass(metric["type"])
        with patch.object(JiraIssues, "max_results", 500):
            return await test_cases_collector_class(self.session, metric).collect()

    async def test_missing_sources(self):
        """Test missing sources."""
        self.assertEqual(None, await self.collect({}))

    async def test_no_test_report(self):
        """Test missing test report."""
        measurement = await self.collect({"jira": {"type": "jira", "parameters": {"url": self.jira_url, "jql": "jql"}}})
        self.assertDictEqual(self.jira_entity(), measurement.sources[0].entities[0])
        self.assertEqual("2", measurement.sources[0].value)

    async def test_matching_test_case_testng(self):
        """Test one matching test case."""
        self.response.text = AsyncMock(return_value=self.TESTNG_XML)
        jira = {"type": "jira", "parameters": {"url": self.jira_url, "jql": "jql"}}
        testng = {"type": "testng", "parameters": {"url": self.test_report_url}}
        measurement = await self.collect({"jira": jira, "testng": testng})
        self.assertListEqual(
            [self.jira_entity(test_result="failed"), self.jira_entity("key-2")],
            measurement.sources[0].entities,
        )
        self.assertEqual("2", measurement.sources[0].value)
        self.assertEqual("0", measurement.sources[1].value)

    async def test_matching_test_case_junit(self):
        """Test one matching test case."""
        self.response.text = AsyncMock(return_value=self.JUNIT_XML)
        jira = {"type": "jira", "parameters": {"url": self.jira_url, "jql": "jql"}}
        junit = {"type": "junit", "parameters": {"url": self.test_report_url}}
        measurement = await self.collect({"jira": jira, "junit": junit})
        self.assertListEqual(
            [self.jira_entity(test_result="failed"), self.jira_entity("key-2")],
            measurement.sources[0].entities,
        )
        self.assertEqual("2", measurement.sources[0].value)
        self.assertEqual("0", measurement.sources[1].value)

    async def test_matching_test_case_robot_framework(self):
        """Test one matching test case."""
        self.response.text = AsyncMock(return_value=self.ROBOT_FRAMEWORK_XML_V4)
        jira = {"type": "jira", "parameters": {"url": self.jira_url, "jql": "jql"}}
        robot_framework = {"type": "robot_framework", "parameters": {"url": self.test_report_url}}
        measurement = await self.collect({"jira": jira, "robot_framework": robot_framework})
        self.assertListEqual(
            [self.jira_entity(test_result="failed"), self.jira_entity("key-2")],
            measurement.sources[0].entities,
        )
        self.assertEqual("2", measurement.sources[0].value)
        self.assertEqual("0", measurement.sources[1].value)

    async def test_matching_test_case_jenkins_test_report(self):
        """Test one marching test case."""
        jenkins_json = {
            "failCount": 1,
            "passCount": 1,
            "suites": [
                {
                    "cases": [
                        {"status": "FAILED", "name": "key-1; tc-1", "className": "c1", "age": 1},
                        {"status": "PASSED", "name": "key-1; tc-1", "className": "c2", "age": 0},
                    ],
                },
            ],
        }
        self.response.json = AsyncMock(side_effect=[[], jenkins_json, self.test_cases_json, self.test_cases_json])
        jira = {"type": "jira", "parameters": {"url": self.jira_url, "jql": "jql"}}
        jenkins_test_report = {"type": "jenkins_test_report", "parameters": {"url": self.test_report_url}}
        measurement = await self.collect({"jira": jira, "jenkins_test_report": jenkins_test_report})
        self.assertListEqual(
            [self.jira_entity(test_result="failed"), self.jira_entity("key-2")],
            measurement.sources[0].entities,
        )
        self.assertEqual("2", measurement.sources[0].value)
        self.assertEqual("0", measurement.sources[1].value)

    async def test_filter_by_test_result(self):
        """Test that test cases can be filtered by test result."""
        self.response.text = AsyncMock(return_value=self.TESTNG_XML)
        jira = {"type": "jira", "parameters": {"url": self.jira_url, "jql": "jql", "test_result": ["untested"]}}
        testng = {"type": "testng", "parameters": {"url": self.test_report_url}}
        measurement = await self.collect({"jira": jira, "testng": testng})
        self.assertListEqual([self.jira_entity("key-2")], measurement.sources[0].entities)
        self.assertEqual("1", measurement.sources[0].value)
        self.assertEqual("0", measurement.sources[1].value)
