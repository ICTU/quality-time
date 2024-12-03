"""Base classes for Robot Framework collector unit tests."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class RobotFrameworkTestCase(SourceCollectorTestCase):
    """Base class for testing Robot Framework collectors."""

    SOURCE_TYPE = "robot_framework"
    ROBOT_FRAMEWORK_XML_V4 = """<?xml version="1.0" encoding="UTF-8"?>
        <robot generator="Robot 4.0b3.dev1 (Python 3.9.1 on linux)" generated="20210212 17:27:03.027">
            <suite id="s1" name="Suite 1">
                <test id="s1-t1" name="Test 1">
                    <status status="FAIL"></status>
                </test>
                <test id="s1-t2" name="Test 2">
                    <status status="PASS"></status>
                </test>
                <doc>Suite 1</doc>
                <status status="FAIL"></status>
            </suite>
            <suite id="s2" name="Suite 2">
                <test id="s2-t1" name="Test 3">
                    <status status="PASS"></status>
                </test>
                <doc>Suite 2</doc>
                <status status="PASS"></status>
            </suite>
            <suite id="s3" name="Suite 3">
                <test id="s3-t1" name="Test 4">
                    <status status="SKIP"></status>
                </test>
                <doc>Suite 3</doc>
                <status status="SKIP"></status>
            </suite>
            <suite><test/></suite>
            <suite><test/><status/></suite>
            <statistics>
                <total>
                    <stat pass="2" fail="1" skip="1">All Tests</stat>
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
                <suite id="s1" name="Suite 1">
                    <test id="s1-t1" name="Test 1">
                        <status status="FAIL"></status>
                    </test>
                    <test id="s1-t2" name="Test 2">
                        <status status="PASS"></status>
                    </test>
                    <doc>Suite 1</doc>
                    <status status="FAIL"></status>
                </suite>
                <suite id="s2" name="Suite 2">
                    <test id="s2-t1" name="Test 3">
                        <status status="PASS"></status>
                    </test>
                    <doc>Suite 2</doc>
                    <status status="PASS"></status>
                </suite>
                <suite id="s3" name="Suite 3">
                    <test id="s3-t1" name="Test 4">
                        <status status="SKIP"></status>
                    </test>
                    <doc>Suite 3</doc>
                    <status status="SKIP"></status>
                </suite>
                <suite><test/></suite>
                <suite><test/><status/></suite>
            </suite>
            <statistics>
                <total>
                    <stat pass="2" fail="1" skip="1">All Tests</stat>
                </total>
            </statistics>
        </robot>"""
    ROBOT_FRAMEWORK_XMLS = ROBOT_FRAMEWORK_XML_V4, ROBOT_FRAMEWORK_XML_V5
