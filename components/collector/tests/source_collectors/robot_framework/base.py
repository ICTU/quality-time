"""Base classes for Robot Framework collector unit tests."""

from ..source_collector_test_case import SourceCollectorTestCase


class RobotFrameworkTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for testing Robot Framework collectors."""

    SOURCE_TYPE = "robot_framework"
    ROBOT_FRAMEWORK_XML_V3 = """<?xml version="1.0"?>
        <robot generator="Robot 3.2.2 (Python 3.9.1 on linux)" generated="20210212 17:27:03.027">
             <suite>
                <test id="s1-t1" name="Test 1">
                    <status status="FAIL"></status>
                </test>
                <test id="s1-t2" name="Test 2">
                    <status status="PASS"></status>
                </test>
            </suite>
            <statistics>
                <total>
                    <stat pass="1" fail="1">Critical Tests</stat>
                    <stat pass="1" fail="1">All Tests</stat>
                </total>
            </statistics>
        </robot>"""
    ROBOT_FRAMEWORK_XML_V4 = """<?xml version="1.0" encoding="UTF-8"?>
        <robot generator="Robot 4.0b3.dev1 (Python 3.9.1 on linux)" generated="20210212 17:27:03.027">
            <suite>
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
