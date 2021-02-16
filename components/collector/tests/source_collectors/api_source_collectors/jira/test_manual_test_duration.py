"""Unit tests for the Jira manual test duration collector."""

from .base import JiraTestCase


class JiraManualTestDurationTest(JiraTestCase):
    """Unit tests for the Jira manual test duration collector."""

    METRIC_TYPE = "manual_test_duration"

    async def test_duration(self):
        """Test that the duration is returned."""
        test_cases_json = dict(
            issues=[self.issue(key="1", field=10), self.issue(key="2", field=15), self.issue(key="3", field=None)]
        )
        response = await self.get_response(test_cases_json)
        self.assert_measurement(
            response,
            value="25",
            entities=[self.entity(key="1", duration="10.0"), self.entity(key="2", duration="15.0")],
        )
