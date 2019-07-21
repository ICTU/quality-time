"""Unit tests for the OJAudit source."""

import unittest
from unittest.mock import Mock, patch

from metric_collectors import MetricCollector


class OJAuditTest(unittest.TestCase):
    """Unit tests for the OJAudit metrics."""

    def setUp(self):
        self.metric = dict(type="violations", addition="sum",
                           sources=dict(a=dict(type="ojaudit", parameters=dict(url="http://ojaudit.xml"))))

    def test_violations(self):
        """Test that the number of violations is returned."""
        mock_response = Mock()
        mock_response.text = """<audit xmlns="http://xmlns.oracle.com/jdeveloper/1013/audit">
  <violation-count>2</violation-count>
  <models>
    <model id="a">
      <file>
        <path>a</path>
      </file>
    </model>
    <model id="b">
      <file>
        <path>b</path>
      </file>
    </model>
  </models>
  <construct>
    <children>
      <construct>
        <children>
          <violation>
            <message>a</message>
            <location model="a">
              <line-number>20</line-number>
              <column-offset>4</column-offset>
            </location>
            <values>
              <value>warning</value>
            </values>
          </violation>
        </children>
      </construct>
      <violation>
        <message>b</message>
        <location model="b">
          <line-number>10</line-number>
              <column-offset>2</column-offset>
        </location>
        <values>
          <value>exception</value>
        </values>
      </violation>
    </children>
  </construct>
</audit>"""
        with patch("requests.get", return_value=mock_response):
            response = MetricCollector(self.metric).get()
        self.assertEqual(
            [dict(component="a:20:4", key="894756a0231a17f66b33d0ac18570daa193beea3", message="a", severity="warning"),
             dict(component="b:10:2", key="2bdb532d49f0bf2252e85dc2d41e034c8c3e1af3", message="b",
                  severity="exception")],
            response["sources"][0]["entities"])
        self.assertEqual("2", response["sources"][0]["value"])

    def test_missing_location(self):
        """Test that an exception is raised if the violation location is missing."""
        mock_response = Mock()
        mock_response.text = """<audit xmlns="http://xmlns.oracle.com/jdeveloper/1013/audit">
  <violation-count>2</violation-count>
  <models>
    <model id="a">
      <file>
        <path>a</path>
      </file>
    </model>
    <model id="b">
      <file>
        <path>b</path>
      </file>
    </model>
  </models>
  <construct>
    <violation>
    <message>a</message>
    <values>
        <value>medium</value>
    </values>
    </violation>
  </construct>
</audit>"""
        with patch("requests.get", return_value=mock_response):
            self.assertTrue(
                "has no location element" in MetricCollector(self.metric).get()["sources"][0]["parse_error"])

    def test_filter_violations(self):
        """Test that violations of types the user doesn't want to see are not included."""
        mock_response = Mock()
        mock_response.text = """<audit xmlns="http://xmlns.oracle.com/jdeveloper/1013/audit">
  <violation-count>1</violation-count>
  <high-count>0</high-count>
  <medium-count>1</medium-count>
  <models>
    <model id="a">
      <file>
        <path>a</path>
      </file>
    </model>
  </models>
  <construct>
    <violation>
      <message>a</message>
      <location model="a">
        <line-number>20</line-number>
        <column-offset>4</column-offset>
      </location>
      <values>
          <value>medium</value>
      </values>
    </violation>
  </construct>
</audit>"""
        self.metric["sources"]["a"]["parameters"]["severities"] = ["high"]
        with patch("requests.get", return_value=mock_response):
            response = MetricCollector(self.metric).get()
        self.assertEqual("0", response["sources"][0]["value"])
        self.assertEqual([], response["sources"][0]["entities"])
