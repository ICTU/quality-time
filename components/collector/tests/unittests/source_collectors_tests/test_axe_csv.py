"""Unit tests for the Axe accessibility analysis report."""

import hashlib
import io
import zipfile

from .source_collector_test_case import SourceCollectorTestCase


class AxeCSVAccessibility(SourceCollectorTestCase):
    """Unit tests for the Axe CSV collector for accessibility violations."""

    def setUp(self):
        super().setUp()
        self.header_row = "URL,Violation Type,Impact,Help,HTML Element,Messages,DOM Element\n"
        self.serious_violation = "url1,aria-input-field-name,serious,help1,html1\n"
        self.moderate_violation = "url2,aria-hidden-focus,moderate,help2,html2,messages2,dom2\n"
        self.csv = self.header_row + self.serious_violation + self.moderate_violation
        self.metric = dict(
            type="accessibility", addition="sum",
            sources=dict(source_id=dict(type="axecsv", parameters=dict(url="https://axecsv"))))
        expected_key1 = hashlib.md5(self.serious_violation.strip().encode("utf-8")).hexdigest()
        expected_key2 = hashlib.md5(self.moderate_violation.strip().encode("utf-8")).hexdigest()
        self.expected_entities = [
            {'description': None, 'element': None, 'help': 'help1', 'impact': 'serious',
             'key': expected_key1, 'page': 'url1', 'url': 'url1', 'violation_type': 'aria-input-field-name'},
            {'description': 'messages2', 'element': 'dom2', 'help': 'help2', 'impact': 'moderate',
             'key': expected_key2, 'page': 'url2', 'url': 'url2', 'violation_type': 'aria-hidden-focus'},
        ]

    def test_nr_of_issues(self):
        """Test that the number of issues is returned."""
        response = self.collect(self.metric, get_request_text=self.csv)
        self.assert_measurement(response, value="2", entities=self.expected_entities)

    def test_no_issues(self):
        """Test zero issues."""
        response = self.collect(self.metric, get_request_text="")
        self.assert_measurement(response, value="0", entities=[])

    def test_filter_by_impact(self):
        """Test that violations can be filtered by impact level."""
        self.metric["sources"]["source_id"]["parameters"]["impact"] = ["serious", "critical"]
        response = self.collect(self.metric, get_request_text=self.csv)
        self.assert_measurement(response, value="1")

    def test_filter_by_violation_type(self):
        """Test that violations can be filtered by violation type."""
        self.metric["sources"]["source_id"]["parameters"]["violation_type"] = \
            ["aria-input-field-name", "area-hidden-focus"]
        response = self.collect(self.metric, get_request_text=self.csv)
        self.assert_measurement(response, value="1")

    def test_zipped_csv(self):
        """Test that a zip archive with CSV files is processed correctly."""
        self.metric["sources"]["source_id"]["parameters"]["url"] = "https://axecsv.zip"
        with zipfile.ZipFile(bytes_io := io.BytesIO(), mode="w") as zipped_axe_csv:
            for index in range(2):
                zipped_axe_csv.writestr(f"axe{index}.csv", self.csv)
        response = self.collect(self.metric, get_request_content=bytes_io.getvalue())
        self.assert_measurement(response, value="4", entities=self.expected_entities + self.expected_entities)
