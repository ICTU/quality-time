"""Base classes for Robot Framework collector unit tests."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class RobotFrameworkTestCase(SourceCollectorTestCase):
    """Base class for testing Robot Framework collectors."""

    SOURCE_TYPE = "robot_framework"
    ROBOT_FRAMEWORK_XML_V4 = """<?xml version="1.0" encoding="UTF-8"?>
        <robot generator="Robot 4.0b3.dev1 (Python 3.9.1 on linux)" generated="20210212 17:27:03.027">
            <suite name="Suite 1">
                <test id="s1-t1" name="Test 1">
                    <status status="FAIL"></status>
                </test>
                <test id="s1-t2" name="Test 2">
                    <status status="PASS"></status>
                </test>
            </suite>
            <statistics>
                <total>
                    <stat pass="1" fail="1" skip="0">All Tests</stat>
                </total>
            </statistics>
        </robot>"""
    ROBOT_FRAMEWORK_XML_V4_WITH_SKIPPED_TESTS = """<?xml version="1.0" encoding="UTF-8"?>
        <robot generator="Robot 4.0b3.dev1 (Python 3.9.1 on linux)" generated="20210212 17:27:03.027">
            <suite name="Suite 1">
                <test id="s1-t1" name="Test 1">
                    <status status="FAIL"></status>
                </test>
                <test id="s1-t2" name="Test 2">
                    <status status="PASS"></status>
                </test>
                <test id="s1-t3" name="Test 3">
                    <status status="SKIP"></status>
                </test>
            </suite>
            <statistics>
                <total>
                    <stat pass="1" fail="1" skip="1">All Tests</stat>
                </total>
            </statistics>
        </robot>"""
    ROBOT_FRAMEWORK_XML_V5 = """<?xml version="1.0" encoding="UTF-8"?>
        <robot
            generator="Robot 7.1.1 (Python 3.12.7 on linux)"
            generated="2021-02-12T17:27:03.027383"
            rpa="false"
            schemaversion="5"
        >
            <suite>
                <suite name="Suite 1">
                    <test id="s1-t1" name="Test 1">
                        <status status="FAIL"></status>
                    </test>
                    <test id="s1-t2" name="Test 2">
                        <status status="PASS"></status>
                    </test>
                </suite>
            </suite>
            <statistics>
                <total>
                    <stat pass="1" fail="1" skip="0">All Tests</stat>
                </total>
            </statistics>
        </robot>"""
    ROBOT_FRAMEWORK_XMLS = ROBOT_FRAMEWORK_XML_V4, ROBOT_FRAMEWORK_XML_V5
