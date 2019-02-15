"""OJAudit metric collector."""

import xml.etree.cElementTree

import requests

from collector.collector import Collector
from collector.type import Measurement, URL


class OJAuditViolations(Collector):
    """Collector to get violations from OJAudit."""

    def api_url(self, **parameters) -> URL:
        return URL(parameters["url"])

    def landing_url(self, **parameters) -> URL:
        return URL(parameters["url"][:-(len("xml"))] + "html")

    def parse_source_response(self, response: requests.Response, **parameters) -> Measurement:
        tree = xml.etree.cElementTree.fromstring(response.text)
        # ElementTree has no API to get the namespace so we extract it from the root tag:
        namespace = tree.tag.split('}')[0][1:]
        violation_count = int(tree.findtext(f"./{{{namespace}}}violation-count"))
        url = self.landing_url(**parameters)
        violations = []
        for construct in tree.findall(f".//{{{namespace}}}construct"):
            construct_name = construct.findtext(f"{{{namespace}}}name")
            for violation in construct.findall(f"./{{{namespace}}}children/{{{namespace}}}violation"):
                message = violation.findtext(f"{{{namespace}}}message")
                line_number = violation.findtext(f".//{{{namespace}}}line-number")
                component = f"{construct_name}:{line_number}"
                violations.append(dict(key=f"{message}:{component}", message=message, component=component, url=url))
        return str(violation_count), violations
