"""Base classes for JUnit XML test report collector unit tests."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class JUnitCollectorTestCase(SourceCollectorTestCase):
    """Base class for Junit collector unit tests."""

    SOURCE_TYPE = "junit"
    JUNIT_XML = """
    <testsuites>
        <testsuite name="ts1" timestamp="2009-12-19T17:58:59" failures="1" errors="1" skipped="1" tests="4">
            <testcase name="tc1" classname="cn"/>
            <testcase name="tc2" classname="cn"><failure/></testcase>
            <testcase name="tc3" classname="cn"><error/></testcase>
            <testcase name="tc4" classname="cn"><skipped/></testcase>
        </testsuite>
        <testsuite name="ts2" timestamp="2009-12-19T17:58:59" failures="0" errors="1" skipped="0" tests="1">
            <testcase name="tc5" classname="cn"><error/></testcase>
        </testsuite>
        <testsuite name="ts3" timestamp="2009-12-19T17:58:59" failures="1" errors="0" skipped="0" tests="1">
            <testcase name="tc6" classname="cn"><failure/></testcase>
        </testsuite>
        <testsuite name="ts4" timestamp="2009-12-19T17:58:59" failures="0" errors="0" skipped="1" tests="1">
            <testcase name="tc7" classname="cn"><skipped/></testcase>
        </testsuite>
        <testsuite name="ts5" timestamp="2009-12-19T17:58:59" failures="0" errors="0" skipped="0" tests="1">
            <testcase name="tc8" classname="cn"></testcase>
        </testsuite>
    </testsuites>"""
    JUNIT_XML_EMPTY_TEST_SUITES = '<testsuites name="Mocha Tests" time="0.0000" tests="0" failures="0"></testsuites>'
