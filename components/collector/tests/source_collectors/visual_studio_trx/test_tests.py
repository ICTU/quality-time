"""Unit tests for the Visual Studio TRX test report tests collector."""

from .base import VisualStudioTRXCollectorTestCase


class VisualStudioTRXTestReportTest(VisualStudioTRXCollectorTestCase):
    """Unit tests for the Visual Studio TRX test report metrics."""

    METRIC_TYPE = "tests"

    def setUp(self):
        """Extend to set up test data."""
        super().setUp()
        self.expected_entities = [
            {
                "key": "446a0829-8d87-1082-ab45-b2ab9f846325",
                "name": "BestaandeZaakOpenen (JIRA-224, JIRA-225)",
                "test_result": "Passed",
                "suite_names": "",
            },
            {
                "key": "63eb0c90-d1fc-a21e-6fc0-3974b0cc65db",
                "name": "BestaandeZaakOpenen2",
                "test_result": "Failed",
                "suite_names": "",
            },
        ]

    async def test_tests(self):
        """Test that the number of tests is returned."""
        response = await self.collect(get_request_text=self.VISUAL_STUDIO_TRX_XML)
        self.assert_measurement(response, value="2", total="2", entities=self.expected_entities)

    async def test_failed_tests(self):
        """Test that the failed tests are returned."""
        self.set_source_parameter("test_result", ["Failed"])
        response = await self.collect(get_request_text=self.VISUAL_STUDIO_TRX_XML)
        entities_for_failed_tests = [entity for entity in self.expected_entities if entity["test_result"] == "Failed"]
        self.assert_measurement(response, value="1", total="2", entities=entities_for_failed_tests)
