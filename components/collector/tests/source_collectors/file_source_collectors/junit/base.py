"""Base classes for JUnit XML test report collector unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class JUnitCollectorTestCase(SourceCollectorTestCase):
    """Base class for Junit collector unit tests."""

    METRIC_TYPE = "Subclass responsibility"
    METRIC_ADDITION = "sum"
    JUNIT_XML = """<testsuites>
    <testsuite timestamp="2009-12-19T17:58:59">
        <testcase name="tc1" classname="cn"/>
        <testcase name="tc2" classname="cn"/>
        <testcase name="tc3" classname="cn"><failure/></testcase>
        <testcase name="tc4" classname="cn"><error/></testcase>
        <testcase name="tc5" classname="cn"><skipped/></testcase>
    </testsuite></testsuites>"""
    JUNIT_URL = "https://junit.xml"

    def setUp(self):
        """Extend to set up the source and metric under test."""
        super().setUp()
        self.sources = dict(source_id=dict(type="junit", parameters=dict(url=self.JUNIT_URL)))
        self.metric = dict(type=self.METRIC_TYPE, sources=self.sources, addition=self.METRIC_ADDITION)
