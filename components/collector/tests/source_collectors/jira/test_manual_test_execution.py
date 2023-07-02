"""Unit tests for the Jira manual test execution collector."""

from datetime import timedelta

from shared.utils.date_time import now

from collector_utilities.date_time import parse_datetime

from .base import JiraTestCase


class JiraManualTestExecutionTest(JiraTestCase):
    """Unit tests for the Jira manual test execution collector."""

    METRIC_TYPE = "manual_test_execution"

    def setUp(self):
        """Extend to create a date in the past."""
        super().setUp()
        self.now = now()
        self.ten_days_ago = str(self.now - timedelta(days=10))

    async def test_nr_of_test_cases(self):
        """Test that the number of test cases is returned."""
        self.set_source_parameter("manual_test_execution_frequency_field", "desired_test_frequency")
        long_ago = "2019-10-02T11:07:02.444+0200"
        test_cases_json = {
            "issues": [
                self.issue(key="1", comment={"comments": [{"updated": long_ago}]}),
                self.issue(key="2", comment={"comments": []}),
                self.issue(key="3", comment={"comments": [{"updated": str(self.now)}]}),
                self.issue(key="4", comment={"comments": [{"updated": self.ten_days_ago}]}, desired_test_frequency="5"),
            ],
        }
        fields_json = [{"name": "Desired test frequency", "id": "desired_test_frequency"}]
        response = await self.get_response(test_cases_json, fields_json)
        self.assert_measurement(
            response,
            value="2",
            entities=[
                self.entity(key="1", last_test_date=str(parse_datetime(long_ago).date()), desired_test_frequency="21"),
                self.entity(
                    key="4",
                    last_test_date=str(parse_datetime(self.ten_days_ago).date()),
                    desired_test_frequency="5",
                ),
            ],
        )

    async def test_nr_of_test_cases_with_field_name(self):
        """Test that the field name for the test frequency can be specified by name."""
        self.set_source_parameter("manual_test_execution_frequency_field", "Required Test Frequency")
        test_cases_json = {
            "issues": [self.issue(comment={"comments": [{"updated": self.ten_days_ago}]}, custom_field_001="5")],
        }
        fields_json = [{"name": "Required test frequency", "id": "custom_field_001"}]
        response = await self.get_response(test_cases_json, fields_json)
        self.assert_measurement(
            response,
            value="1",
            entities=[
                self.entity(
                    key="1",
                    last_test_date=str(parse_datetime(self.ten_days_ago).date()),
                    desired_test_frequency="5",
                ),
            ],
        )

    async def test_nr_of_test_cases_without_field_name(self):
        """Test that the field name is optional."""
        self.set_source_parameter("manual_test_execution_frequency_default", "5")
        test_cases_json = {"issues": [self.issue(comment={"comments": [{"updated": self.ten_days_ago}]})]}
        fields_json = [{"name": "Desired test frequency", "id": "desired_test_frequency"}]
        response = await self.get_response(test_cases_json, fields_json)
        self.assert_measurement(
            response,
            value="1",
            entities=[
                self.entity(
                    key="1",
                    last_test_date=str(parse_datetime(self.ten_days_ago).date()),
                    desired_test_frequency="5",
                ),
            ],
        )
