"""Unit tests for the test cases metric collector."""

import unittest
from typing import Optional
from unittest.mock import AsyncMock

from metric_collectors import TestCases
from model import MetricMeasurement

from ..data_model_fixture import DATA_MODEL


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

    def setUp(self) -> None:  # pylint: disable=invalid-name
        """Extend to set up test fixtures."""
        super().setUp()
        self.session = AsyncMock()
        self.response = self.session.get.return_value = AsyncMock()
        test_cases_json = dict(total=2, issues=[self.jira_issue(), self.jira_issue("key-2")])
        self.response.json = AsyncMock(side_effect=[[], test_cases_json, test_cases_json])
        self.jira_url = "https://jira"
        self.testng_url = "https://testng"
        self.junit_url = "https://junit"
        self.robot_framework_url = "https://robot"

    def jira_issue(self, key="key-1", **fields):
        """Create a Jira issue."""
        return dict(id=key, key=key, fields=dict(created=self.CREATED, summary=f"Summary {key}", **fields))

    def jira_entity(self, key="key-1", test_result="untested"):
        """Create an entity."""
        return dict(
            key=key,
            issue_key=key,
            summary=f"Summary {key}",
            url=f"{self.jira_url}/browse/{key}",
            created=self.CREATED,
            updated=None,
            status=None,
            priority=None,
            type="Unknown issue type",
            test_result=test_result,
        )

    async def collect(self, sources) -> Optional[MetricMeasurement]:
        """Collect the measurement."""
        metric = dict(type="test_cases", sources=sources)
        return await TestCases(self.session, metric, DATA_MODEL).collect()

    async def test_missing_sources(self):
        """Test missing sources."""
        self.assertEqual(None, await self.collect({}))

    async def test_no_test_report(self):
        """Test missing test report."""
        measurement = await self.collect(dict(jira=dict(type="jira", parameters=dict(url=self.jira_url))))
        self.assertDictEqual(self.jira_entity(), measurement.sources[0].entities[0])
        self.assertEqual("2", measurement.sources[0].value)

    async def test_matching_test_case_testng(self):
        """Test one matching test case."""
        self.response.text = AsyncMock(return_value=self.TESTNG_XML)
        jira = dict(type="jira", parameters=dict(url=self.jira_url))
        testng = dict(type="testng", parameters=dict(url=self.testng_url))
        measurement = await self.collect(dict(jira=jira, testng=testng))
        self.assertListEqual(
            [self.jira_entity(test_result="failed"), self.jira_entity("key-2")], measurement.sources[0].entities
        )
        self.assertEqual("2", measurement.sources[0].value)
        self.assertEqual("0", measurement.sources[1].value)

    async def test_matching_test_case_junit(self):
        """Test one matching test case."""
        self.response.text = AsyncMock(return_value=self.JUNIT_XML)
        jira = dict(type="jira", parameters=dict(url=self.jira_url))
        junit = dict(type="junit", parameters=dict(url=self.junit_url))
        measurement = await self.collect(dict(jira=jira, junit=junit))
        self.assertListEqual(
            [self.jira_entity(test_result="failed"), self.jira_entity("key-2")], measurement.sources[0].entities
        )
        self.assertEqual("2", measurement.sources[0].value)
        self.assertEqual("0", measurement.sources[1].value)

    async def test_matching_test_case_robot_framework(self):
        """Test one matching test case."""
        self.response.text = AsyncMock(return_value=self.ROBOT_FRAMEWORK_XML_V4)
        jira = dict(type="jira", parameters=dict(url=self.jira_url))
        robot_framework = dict(type="robot_framework", parameters=dict(url=self.robot_framework_url))
        measurement = await self.collect(dict(jira=jira, robot_framework=robot_framework))
        self.assertListEqual(
            [self.jira_entity(test_result="failed"), self.jira_entity("key-2")], measurement.sources[0].entities
        )
        self.assertEqual("2", measurement.sources[0].value)
        self.assertEqual("0", measurement.sources[1].value)

    async def test_filter_by_test_result(self):
        """Test that test cases can be filtered by test result."""
        self.response.text = AsyncMock(return_value=self.TESTNG_XML)
        jira = dict(type="jira", parameters=dict(url=self.jira_url, test_result=["untested"]))
        testng = dict(type="testng", parameters=dict(url=self.testng_url))
        measurement = await self.collect(dict(jira=jira, testng=testng))
        self.assertListEqual([self.jira_entity("key-2")], measurement.sources[0].entities)
        self.assertEqual("1", measurement.sources[0].value)
        self.assertEqual("0", measurement.sources[1].value)
