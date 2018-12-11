"""JUnit metric source."""

import xml.etree.cElementTree

import requests

from quality_time.source import Source
from quality_time.type import Measurement


class JUnitTests(Source):
    """Source class to get the number of tests from JUnit XML reports."""

    def parse_source_response(self, response: requests.Response) -> Measurement:
        tree = xml.etree.cElementTree.fromstring(response.text)
        test_suites = [tree] if tree.tag == "testsuite" else tree.findall("testsuite")
        return Measurement(sum(int(test_suite.get("tests", 0)) for test_suite in test_suites))


class JUnitFailedTests(Source):
    """Source class to get the number of failed tests from JUnit XML reports."""

    def parse_source_response(self, response: requests.Response) -> Measurement:
        tree = xml.etree.cElementTree.fromstring(response.text)
        test_suites = [tree] if tree.tag == "testsuite" else tree.findall("testsuite")
        return Measurement(sum(int(test_suite.get("failures", 0)) for test_suite in test_suites))
