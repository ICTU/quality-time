"""OWASP Dependency Check metric collector."""

from xml.etree.cElementTree import Element

import requests

from ..collector import Collector
from ..type import Namespaces, URL, Value
from ..util import parse_source_response_xml


class OWASPDependencyCheckSecurityWarnings(Collector):
    """Collector to get security warnings from OWASP Dependency Check."""

    def landing_url(self, **parameters) -> URL:
        return URL(parameters["url"][:-(len("xml"))] + "html")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        tree, namespaces = parse_source_response_xml(response)
        return self.violation_count(tree, namespaces)

    @staticmethod
    def violation_count(tree: Element, namespaces: Namespaces) -> str:
        """Return the violation count."""
        dependencies = tree.findall(f".//ns:dependency/ns:vulnerabilities/ns:vulnerability", namespaces)
        return str(len(dependencies))
