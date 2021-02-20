"""Unit tests for the Performancetest-runner performance test stability collector."""

from .base import PerformanceTestRunnerTestCase


class PerformanceTestRunnerStabilityTest(PerformanceTestRunnerTestCase):
    """Unit tests for the Performancetest-runner performance test stability collector."""

    METRIC_TYPE = "performancetest_stability"
    METRIC_ADDITION = "min"

    async def test_stability(self):
        """Test that the percentage of the duration at which the performance test becomes unstable is returned."""
        html = """<html><table class="config">
            <tr><td class="name">Trendbreak 'stability' (%)</td><td id="trendbreak_stability">90</td></tr>
            </table></html>"""
        response = await self.collect(self.metric, get_request_text=html)
        self.assert_measurement(response, value="90")
