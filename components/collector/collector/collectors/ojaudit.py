"""OJAudit metric collector."""

import hashlib
import xml.etree.cElementTree
from xml.etree.cElementTree import Element
from typing import Dict, List

import requests

from collector.collector import Collector
from collector.type import Measurement, URL


Namespaces = Dict[str, str]  # Namespace prefix to Namespace URI mapping
ModelFilePaths = Dict[str, str]  # Model id to model file path mapping
Violation = Dict[str, str]  # Violation attribute key to attribute value mapping


class OJAuditViolations(Collector):
    """Collector to get violations from OJAudit."""

    def api_url(self, **parameters) -> URL:
        return URL(parameters["url"])

    def landing_url(self, **parameters) -> URL:
        return URL(parameters["url"][:-(len("xml"))] + "html")

    def parse_source_response(self, response: requests.Response, **parameters) -> Measurement:
        tree = xml.etree.cElementTree.fromstring(response.text)
        # ElementTree has no API to get the namespace so we extract it from the root tag:
        namespaces = dict(ns=tree.tag.split('}')[0][1:])
        violation_count = tree.findtext(f"./ns:violation-count", namespaces=namespaces)
        models = self.model_file_paths(tree, namespaces)
        violations = self.violations(tree, namespaces, models)
        return violation_count, violations

    def violations(self, tree: Element, namespaces: Namespaces, models: ModelFilePaths) -> List[Violation]:
        """Return the violations."""
        violation_elements = tree.findall(f".//ns:violation", namespaces)
        return [self.violation(violation_element, namespaces, models) for violation_element in violation_elements]

    @staticmethod
    def violation(violation: Element, namespaces: Namespaces, models: ModelFilePaths) -> Violation:
        """Return the violation as unit."""
        location = violation.find("./ns:location", namespaces)
        if not location:
            raise ValueError(f"OJAudit violation {violation} has no location element")
        model = models[location.get("model")]
        message = violation.findtext("ns:message", namespaces=namespaces)
        line_number = violation.findtext(".//ns:line-number", namespaces=namespaces)
        column_offset = violation.findtext(".//ns:column-offset", namespaces=namespaces)
        severity = violation.findtext("./ns:values/ns:value", namespaces=namespaces)
        component = f"{model}:{line_number}:{column_offset}"
        key = hashlib.sha1(f"{message}:{component}".encode("utf-8")).hexdigest()
        return dict(key=key, severity=severity, message=message, component=component)

    @staticmethod
    def model_file_paths(tree: Element, namespaces: Namespaces) -> ModelFilePaths:
        """Return the model file paths."""
        models = tree.findall(".//ns:model", namespaces)
        return {model.get("id"): model.findtext("./ns:file/ns:path", namespaces=namespaces) for model in models}
