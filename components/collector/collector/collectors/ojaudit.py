"""OJAudit metric collector."""

import hashlib
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
        models = {}
        for model in tree.findall(f".//{{{namespace}}}model"):
            model_file_path = model.findtext(f"./{{{namespace}}}file/{{{namespace}}}path")
            models[model.get("id")] = model_file_path
        violations = []
        for violation in tree.findall(f".//{{{namespace}}}violation"):
            location = violation.find(f"./{{{namespace}}}location")
            model_id = location.get("model")
            message = violation.findtext(f"{{{namespace}}}message")
            line_number = violation.findtext(f".//{{{namespace}}}line-number")
            column_offset = violation.findtext(f".//{{{namespace}}}column-offset")
            severity = violation.findtext(f"./{{{namespace}}}values/{{{namespace}}}value")
            component = f"{models[model_id]}:{line_number}:{column_offset}"
            violations.append(dict(
                key=hashlib.md5(f"{message}:{component}".encode("utf-8")).hexdigest(),
                severity=severity, message=message, component=component))
        return str(violation_count), violations
