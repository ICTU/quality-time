"""Unit tests for the NCover source."""

import io
import zipfile
from datetime import datetime

from .source_collector_test_case import SourceCollectorTestCase


class NCoverTest(SourceCollectorTestCase):
    """Unit tests for the NCover metrics."""

    def setUp(self):
        super().setUp()
        self.sources = dict(source_id=dict(type="ncover", parameters=dict(url="https://ncover/report.html")))
        self.ncover_html = """<script type="text/javascript">
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

    def test_uncovered_lines(self):
        """Test that the number of uncovered sequence points is returned."""
        metric = dict(type="uncovered_lines", sources=self.sources, addition="sum")
        response = self.collect(metric, get_request_text=self.ncover_html)
        self.assert_measurement(response, value=f"{17153-14070}", total="17153")

    def test_uncovered_branches(self):
        """Test that the number of uncovered branches is returned."""
        metric = dict(type="uncovered_branches", sources=self.sources, addition="sum")
        response = self.collect(metric, get_request_text="""
            <script type="text/javascript">
                Other javascript
            </script>
            <script type="text/javascript">
                ncover.execution.stats = {
                    "branchCoverage": {
                        "coveragePoints": 12034,
                        "coveredPoints": 9767
                    }
                };
            </script>""")
        self.assert_measurement(response, value=f"{12034-9767}", total="12034")

    def test_zipped_report(self):
        """Test that the coverage can be read from a zip with NCover reports."""
        self.sources["source_id"]["parameters"]["url"] = "https://report.zip"
        metric = dict(type="uncovered_lines", sources=self.sources, addition="sum")
        with zipfile.ZipFile(bytes_io := io.BytesIO(), mode="w") as zipped_ncover_report:
            zipped_ncover_report.writestr("ncover.html", self.ncover_html)
        response = self.collect(metric, get_request_content=bytes_io.getvalue())
        self.assert_measurement(response, value=f"{17153-14070}", total="17153")

    def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="sum")
        response = self.collect(metric, get_request_text="""
         <script type="text/javascript">
            ncover.serverRoot = 'http://127.0.0.1:11235';
            ncover.createDateTime = '1440425155042';
        </script>""")
        report_datetime = datetime.fromtimestamp(1440425155042 / 1000.)
        expected_age = (datetime.now(tz=report_datetime.tzinfo) - report_datetime).days
        self.assert_measurement(response, value=str(expected_age))
