"""Unit tests for the JUnit XML test report source."""

from datetime import datetime

from .source_collector_test_case import SourceCollectorTestCase


class JUnitTestReportTest(SourceCollectorTestCase):
    """Unit tests for the JUnit XML test report metrics."""

    def setUp(self):
        super().setUp()
        self.sources = dict(
            source_id=dict(type="junit", parameters=dict(url="junit.xml", test_result=["failed", "errored", "passed"])))
        self.metric = dict(type="tests", sources=self.sources, addition="sum")
        self.junit_xml = """<testsuites>
        <testsuite>
            <testcase name="tc1" classname="cn"/>
            <testcase name="tc2" classname="cn"/>
            <testcase name="tc3" classname="cn"><failure/></testcase>
            <testcase name="tc4" classname="cn"><error/></testcase>
            <testcase name="tc5" classname="cn"><skipped/></testcase>
        </testsuite></testsuites>"""

    def test_tests(self):
        """Test that the number of tests is returned."""
        response = self.collect(self.metric, get_request_text=self.junit_xml)
        self.assert_value("4", response)
        self.assert_entities(
            [
                dict(key="tc1", name="tc1", class_name="cn", test_result="passed"),
                dict(key="tc2", name="tc2", class_name="cn", test_result="passed"),
                dict(key="tc3", name="tc3", class_name="cn", test_result="failed"),
                dict(key="tc4", name="tc4", class_name="cn", test_result="errored")
            ],
            response)


class JunitTestReportFailedTestsTest(SourceCollectorTestCase):
    """Unit tests for the failed test metric."""

    def setUp(self):
        super().setUp()
        self.sources = dict(source_id=dict(type="junit", parameters=dict(url="junit.xml")))
        self.metric = dict(type="failed_tests", sources=self.sources, addition="sum")

    def test_failed_tests(self):
        """Test that the failed tests are returned."""
        response = self.collect(
            self.metric,
            get_request_text="""<testsuites><testsuite failures="1"><testcase name="tc" classname="cn"><failure/>
            </testcase></testsuite></testsuites>""")
        self.assert_value("1", response)
        self.assert_entities([dict(key="tc", name="tc", class_name="cn", failure_type="failed")], response)


class JUnitSourceUpToDatenessTest(SourceCollectorTestCase):
    """Unit test for the source up-to-dateness metric."""

    def setUp(self):
        super().setUp()
        self.sources = dict(source_id=dict(type="junit", parameters=dict(url="junit.xml")))

    def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="max")
        response = self.collect(
            metric, get_request_text='<?xml version="1.0"?><testsuite timestamp="2009-12-19T17:58:59"></testsuite>')
        expected_age = (datetime.now() - datetime(2009, 12, 19, 17, 58, 59)).days
        self.assert_value(str(expected_age), response)
