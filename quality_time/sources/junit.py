"""JUnit metric source."""

import xml.etree.cElementTree
from typing import Type

import requests

from quality_time.metric import Metric
from quality_time.metrics import FailedTests, Tests
from quality_time.source import Source
from quality_time.type import Measurement


class JUnit(Source):
    """Source class to get measurements from JUnit XML reports."""

    API = "junit"

    @classmethod
    def convert_metric_name(cls, metric: Type[Metric]) -> str:
        return {FailedTests: "failures", Tests: "tests"}[metric]

    @classmethod
    def parse_source_response(cls, metric: str, response: requests.Response) -> Measurement:
        tree = xml.etree.cElementTree.fromstring(response.text)
        test_suites = [tree] if tree.tag == "testsuite" else tree.findall("testsuite")
        return Measurement(sum(int(test_suite.get(metric, 0)) for test_suite in test_suites))
