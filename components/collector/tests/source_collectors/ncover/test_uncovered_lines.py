"""Unit tests for the NCover uncovered lines collector."""

from .base import NCoverTestCase


class NCoverUncoveredLinesTest(NCoverTestCase):
    """Unit tests for the NCover uncovered lines collector."""

    METRIC_TYPE = "uncovered_lines"
    NCOVER_HTML = """<script type="text/javascript">
            Other javascript
        </script>
        <script type="text/javascript">
            ncover.execution.stats = {
                "sequencePointCoverage": {
                    "coveragePoints": 17153,
                    "coveredPoints": 14070
                }
            };
        </script>"""

    async def test_uncovered_lines(self):
        """Test that the number of uncovered sequence points is returned."""
        response = await self.collect(self.metric, get_request_text=self.NCOVER_HTML)
        self.assert_measurement(response, value=f"{17153-14070}", total="17153")

    async def test_zipped_report(self):
        """Test that the coverage can be read from a zip with NCover reports."""
        self.set_source_parameter("url", "https://report.zip")
        response = await self.collect(
            self.metric, get_request_content=self.zipped_report("ncover.html", self.NCOVER_HTML)
        )
        self.assert_measurement(response, value=f"{17153-14070}", total="17153")
