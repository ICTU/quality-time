"""Unit tests for the Axe accessibility analysis report."""

import hashlib

from .source_collector_test_case import SourceCollectorTestCase


class AxeCSVAccessibility(SourceCollectorTestCase):
    """Unit tests for the Axe CSV collector for accessibility violations."""

    def setUp(self):
        super().setUp()
        self.header_row = "URL,Violation Type,Impact,Help,HTML Element,Messages,DOM Element\n"
        self.metric = dict(
            type="accessibility",
            sources=dict(
                source_id=dict(
                    type="axecsv", parameters=dict(url="https://axecsv", private_token="xxx"))), addition="sum")

    def test_nr_of_issues(self):
        """Test that the number of issues is returned."""
        response = self.collect(
            self.metric, get_request_text=self.header_row + "1,2,serious,6,7\n11,12,moderate,14,15,16,17")
        self.assert_measurement(response, value="2")

    def test_no_issues(self):
        """Test zero issues."""
        response = self.collect(self.metric, get_request_text="")
        self.assert_measurement(response, value="0")

    def test_issues(self):
        """Test that the issues are returned."""
        csv_row = "https://axe/1,2,critical,4,5,6,7"
        response = self.collect(self.metric, get_request_text=self.header_row + csv_row)
        expected_key = hashlib.md5(csv_row.encode("utf-8")).hexdigest()
        self.assert_measurement(
            response,
            entities=[
                {'description': '6', 'element': '7', 'help': '4', 'impact': 'critical',
                 'key': expected_key, 'page': '/1', 'url': 'https://axe/1',
                 'violation_type': '2'}])

    def test_filter_by_impact(self):
        """Test that violations can be filtered by impact level."""
        self.metric["sources"]["source_id"]["parameters"]["impact"] = ["serious", "critical"]
        response = self.collect(
            self.metric, get_request_text=self.header_row + "1,2,serious,6,7\n11,12,moderate,14,15,16,17")
        self.assert_measurement(response, value="1")
