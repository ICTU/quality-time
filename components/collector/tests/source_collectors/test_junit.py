"""Unit tests for the JUnit XML test report source."""

import io
import zipfile
from datetime import datetime

from .source_collector_test_case import SourceCollectorTestCase


class JUnitTestReportTest(SourceCollectorTestCase):
    """Unit tests for the JUnit XML test report metrics."""

    def setUp(self):
        super().setUp()
        self.sources = dict(source_id=dict(type="junit", parameters=dict(url="junit.xml")))
        self.metric = dict(type="tests", sources=self.sources, addition="sum")
        self.junit_xml = """<testsuites>
        <testsuite>
            <testcase name="tc1" classname="cn"/>
            <testcase name="tc2" classname="cn"/>
            <testcase name="tc3" classname="cn"><failure/></testcase>
            <testcase name="tc4" classname="cn"><error/></testcase>
            <testcase name="tc5" classname="cn"><skipped/></testcase>
        </testsuite></testsuites>"""
        self.expected_entities = [
            dict(key="tc1", name="tc1", class_name="cn", test_result="passed"),
            dict(key="tc2", name="tc2", class_name="cn", test_result="passed"),
            dict(key="tc3", name="tc3", class_name="cn", test_result="failed"),
            dict(key="tc4", name="tc4", class_name="cn", test_result="errored"),
            dict(key="tc5", name="tc5", class_name="cn", test_result="skipped")]

    def test_tests(self):
        """Test that the number of tests is returned."""
        response = self.collect(self.metric, get_request_text=self.junit_xml)
        self.assert_measurement(response, value="5", entities=self.expected_entities)

    def test_failed_tests(self):
        """Test that the failed tests are returned."""
        self.sources["source_id"]["parameters"]["test_result"] = ["failed"]
        response = self.collect(self.metric, get_request_text=self.junit_xml)
        self.assert_measurement(
            response, value="1", entities=[dict(key="tc3", name="tc3", class_name="cn", test_result="failed")])

    def test_zipped_junit_report(self):
        """Test that the number of tests is returned from a zip with JUnit reports."""
        self.sources["source_id"]["parameters"]["url"] = "junit.zip"
        with zipfile.ZipFile(bytes_io := io.BytesIO(), mode="w") as zipped_bandit_report:
            zipped_bandit_report.writestr("junit.xml", self.junit_xml)
        response = self.collect(self.metric, get_request_content=bytes_io.getvalue())
        self.assert_measurement(response, value="5", entities=self.expected_entities)


class JUnitSourceUpToDatenessTest(SourceCollectorTestCase):
    """Unit tests for the source up-to-dateness metric."""

    def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        sources = dict(source_id=dict(type="junit", parameters=dict(url="junit.xml")))
        metric = dict(type="source_up_to_dateness", sources=sources, addition="max")
        response = self.collect(
            metric, get_request_text='<?xml version="1.0"?><testsuite timestamp="2009-12-19T17:58:59"></testsuite>')
        expected_age = (datetime.now() - datetime(2009, 12, 19, 17, 58, 59)).days
        self.assert_measurement(response, value=str(expected_age))
