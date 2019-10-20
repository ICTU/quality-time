"""Unit tests for the Axe accessibility analysis report."""

from .source_collector_test_case import SourceCollectorTestCase


class AxeCSVAccessibility(SourceCollectorTestCase):
    """Unit tests for the Axe CSV collector for accessibility violations."""

    def setUp(self):
        super().setUp()
        self.metric = dict(
            type="accessibility",
            sources=dict(
                source_id=dict(
                    type="axecsv", parameters=dict(url="https://axecsv", private_token="xxx"))), addition="sum")

    def test_nr_of_issues(self):
        """Test that the number of issues is returned."""
        response = self.collect(
            self.metric,
            get_request_text="URL,Violation Type,Impact,Help,HTML Element,Messages,DOM Element"
                             "\n1,2,,6,7\n11,12,13,14,15,16,17")
        self.assert_measurement(response, value="2")

    def test_no_issues(self):
        """Test zero issues."""
        response = self.collect(self.metric, get_request_text="")
        self.assert_measurement(response, value="0")

    def test_issues(self):
        """Test that the issues are returned."""
        response = self.collect(
            self.metric,
            get_request_text="URL,Violation Type,Impact,Help,HTML Element,Messages,DOM Element\n"
                             "https://axe/1,2,3,4,5,6,7")
        self.assert_measurement(
            response,
            entities=[
                {'description': '6', 'element': '7', 'help': '4', 'impact': '3',
                 'key': '5d0145560fdc31509774775cbf2a8ff0', 'page': '/1', 'url': 'https://axe/1',
                 'violation_type': '2'}])
