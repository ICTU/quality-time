"""Unit tests for the JUnit XML test report source."""

from datetime import datetime

from .source_collector_test_case import SourceCollectorTestCase


class JunitTestReportTestCase(SourceCollectorTestCase):
    """Base class for JUnit test report collector unit tests."""

    def setUp(self):
        super().setUp()
        self.sources = dict(source_id=dict(type="junit", parameters=dict(url="junit.xml")))


class JUnitTestReportTest(JunitTestReportTestCase):
    """Unit tests for the JUnit XML test report metrics."""

    def test_tests(self):
        """Test that the number of tests is returned."""
        metric = dict(type="tests", sources=self.sources, addition="sum")
        response = self.collect(metric, get_request_text='<testsuites><testsuite tests="2"></testsuite></testsuites>')
        self.assert_value("2", response)


class JunitTestReportFailedTestsTest(JunitTestReportTestCase):
    """Unit tests for the failed test metric."""

    def setUp(self):
        super().setUp()
        self.metric = dict(type="failed_tests", sources=self.sources, addition="sum")

    def test_failed_tests(self):
        """Test that the number of failed tests is returned."""
        response = self.collect(
            self.metric, get_request_text='<testsuites><testsuite failures="3"></testsuite></testsuites>')
        self.assert_value("3", response)

    def test_failed_tests_entities(self):
        """Test that the failed tests are returned as entities."""
        response = self.collect(
            self.metric,
            get_request_text="""<testsuites><testsuite failures="1"><testcase name="tc" classname="cn"><failure/>
            </testcase></testsuite></testsuites>""")
        self.assert_entities([dict(key="tc", name="tc", class_name="cn", failure_type="failed")], response)


class JUnitSourceUpToDatenessTest(JunitTestReportTestCase):
    """Unit test for the source up-to-dateness metric."""

    def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="max")
        response = self.collect(
            metric, get_request_text='<?xml version="1.0"?><testsuite timestamp="2009-12-19T17:58:59"></testsuite>')
        expected_age = (datetime.now() - datetime(2009, 12, 19, 17, 58, 59)).days
        self.assert_value(str(expected_age), response)
