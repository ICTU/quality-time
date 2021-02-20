"""Unit tests for the Jira manual test execution collector."""

from datetime import datetime, timedelta

from dateutil.parser import parse

from .base import JiraTestCase


class JiraManualTestExecutionTest(JiraTestCase):
    """Unit tests for the Jira manual test execution collector."""

    METRIC_TYPE = "manual_test_execution"

    def setUp(self):
        """Extend to create a date in the past."""
        super().setUp()
        self.ten_days_ago = str(datetime.now() - timedelta(days=10))

    async def test_nr_of_test_cases(self):
        """Test that the number of test cases is returned."""
        long_ago = "2019-10-02T11:07:02.444+0200"
        test_cases_json = dict(
            issues=[
                self.issue(key="1", comment=dict(comments=[dict(updated=long_ago)])),
                self.issue(key="2", comment=dict(comments=[])),
                self.issue(key="3", comment=dict(comments=[dict(updated=str(datetime.now()))])),
                self.issue(
                    key="4", comment=dict(comments=[dict(updated=self.ten_days_ago)]), desired_test_frequency="5"
                ),
            ]
        )
        response = await self.get_response(test_cases_json)
        self.assert_measurement(
            response,
            value="2",
            entities=[
                self.entity(key="1", last_test_date=str(parse(long_ago).date()), desired_test_frequency="21"),
                self.entity(key="4", last_test_date=str(parse(self.ten_days_ago).date()), desired_test_frequency="5"),
            ],
        )

    async def test_nr_of_test_cases_with_field_name(self):
        """Test that the field name for the test frequency can be specified by name."""
        self.set_source_parameter("manual_test_execution_frequency_field", "Required Test Frequency")
        test_cases_json = dict(
            issues=[self.issue(comment=dict(comments=[dict(updated=self.ten_days_ago)]), custom_field_001="5")]
        )
        fields_json = [dict(name="Required test frequency", id="custom_field_001")]
        response = await self.get_response(test_cases_json, fields_json)
        self.assert_measurement(
            response,
            value="1",
            entities=[
                self.entity(key="1", last_test_date=str(parse(self.ten_days_ago).date()), desired_test_frequency="5")
            ],
        )
