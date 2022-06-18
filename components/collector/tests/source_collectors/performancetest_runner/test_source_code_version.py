"""Unit tests for the Performancetest-runner source code version collector."""

from .base import PerformanceTestRunnerTestCase


class PerformanceTestRunnerSourceCodeVersionTest(PerformanceTestRunnerTestCase):
    """Unit tests for the Performancetest-runner source code version collector."""

    METRIC_TYPE = "source_code_version"
    METRIC_ADDITION = "min"

    async def test_source_code_version(self):
        """Test that the version is returned."""
        html = (
            '<html><table class="config"><tr><td class="name">Application version</td>'
            '<td id="application_version">1.2.3</td></tr></table></html>'
        )
        response = await self.collect(get_request_text=html)
        self.assert_measurement(response, value="1.2.3")
