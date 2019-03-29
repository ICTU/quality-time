"""OJAudit metric collector."""

import hashlib
from xml.etree.cElementTree import Element
from typing import Dict, List, Optional

import requests

from ..collector import Collector
from ..type import Namespaces, URL, Units, Value
from ..util import parse_source_response_xml


ModelFilePaths = Dict[str, str]  # Model id to model file path mapping
Violation = Dict[str, str]  # Violation attribute key to attribute value mapping


class OJAuditViolations(Collector):
    """Collector to get violations from OJAudit."""

    def landing_url(self, **parameters) -> URL:
        return URL(parameters["url"][:-(len("xml"))] + "html")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        tree, namespaces = parse_source_response_xml(response)
        severities = parameters.get("severities", [])
        return self.violation_count(tree, namespaces, severities)

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        tree, namespaces = parse_source_response_xml(response)
        severities = parameters.get("severities", [])
        return self.violations(tree, namespaces, severities)

    @staticmethod
    def violation_count(tree: Element, namespaces: Namespaces, severities: List[str]) -> str:
        """Return the violation count."""
        count = 0
        for severity in severities or ["violation"]:
            count += int(tree.findtext(f"./ns:{severity}-count", namespaces=namespaces))
        return str(count)

    def violations(self, tree: Element, namespaces: Namespaces, severities: List[str]) -> List[Violation]:
        """Return the violations."""
        models = self.model_file_paths(tree, namespaces)
        violation_elements = tree.findall(f".//ns:violation", namespaces)
        violations = [self.violation(element, namespaces, models, severities) for element in violation_elements]
        return [violation for violation in violations if violation is not None]

    @staticmethod
    def violation(violation: Element, namespaces: Namespaces, models: ModelFilePaths,
                  severities: List[str]) -> Optional[Violation]:
        """Return the violation as unit."""
        location = violation.find("./ns:location", namespaces)
        if not location:
            raise ValueError(f"OJAudit violation {violation} has no location element")
        severity = violation.findtext("./ns:values/ns:value", namespaces=namespaces)
        if severities and severity not in severities:
            return None
        message = violation.findtext("ns:message", namespaces=namespaces)
        line_number = violation.findtext(".//ns:line-number", namespaces=namespaces)
        column_offset = violation.findtext(".//ns:column-offset", namespaces=namespaces)
        model = models[location.get("model")]
        component = f"{model}:{line_number}:{column_offset}"
        key = hashlib.sha1(f"{message}:{component}".encode("utf-8")).hexdigest()
        return dict(key=key, severity=severity, message=message, component=component)

    @staticmethod
    def model_file_paths(tree: Element, namespaces: Namespaces) -> ModelFilePaths:
        """Return the model file paths."""
        models = tree.findall(".//ns:model", namespaces)
        return {model.get("id"): model.findtext("./ns:file/ns:path", namespaces=namespaces) for model in models}
