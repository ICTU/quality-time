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

    def setUp(self) -> None:  # pylint: disable=invalid-name
        """Extend to set up test fixtures."""
        super().setUp()
        self.session = AsyncMock()
        self.response = self.session.get.return_value = AsyncMock()
        self.jira_url = "https://jira"
        self.testng_url = "https://testng"
        self.created = "2020-08-06T16:36:48.000+0200"

    def jira_issue(self, key="key-1", **fields):
        """Create a Jira issue."""
        return dict(id=key, key=key, fields=dict(created=self.created, summary=f"Summary {key}", **fields))

    def jira_entity(self, key="key-1", created=None, updated=None, issuetype="Unknown issue type", **kwargs):
        """Create an entity."""
        return dict(
            key=key,
            issue_key=key,
            summary=f"Summary {key}",
            url=f"{self.jira_url}/browse/{key}",
            created=created or self.created,
            updated=updated,
            status=None,
            priority=None,
            type=issuetype,
            **kwargs,
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
        test_cases_json = dict(total=1, issues=[self.jira_issue()])
        self.response.json = AsyncMock(side_effect=[[], test_cases_json])
        measurement = await self.collect(dict(jira=dict(type="jira", parameters=dict(url=self.jira_url))))
        self.assertDictEqual(self.jira_entity(), measurement.sources[0].entities[0])

    async def test_matching_tests(self):
        """Test one matching test cases."""
        test_cases_json = dict(total=1, issues=[self.jira_issue()])
        self.response.json = AsyncMock(side_effect=[[], test_cases_json])
        self.response.text = AsyncMock(return_value=self.TESTNG_XML)
        jira = dict(type="jira", parameters=dict(url=self.jira_url))
        testng = dict(type="testng", parameters=dict(url=self.testng_url))
        measurement = await self.collect(dict(jira=jira, testng=testng))
        self.assertDictEqual(self.jira_entity(test_result="failed"), measurement.sources[0].entities[0])
        self.assertEqual("0", measurement.sources[1].value)
