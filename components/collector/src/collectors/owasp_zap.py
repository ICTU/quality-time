"""OWASP ZAP metric collector."""

from xml.etree.cElementTree import Element

import requests

from ..collector import Collector
from ..type import Namespaces, URL, Value
from ..util import parse_source_response_xml


class OWASPZAPSecurityWarnings(Collector):
    """Collector to get security warnings from OWASP ZAP."""

    def landing_url(self, **parameters) -> URL:
        return URL(parameters["url"][:-(len("xml"))] + "html")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        tree, namespaces = parse_source_response_xml(response)
        return self.warning_count(tree, namespaces)

    @staticmethod
    def warning_count(tree: Element, namespaces: Namespaces) -> str:
        """Return the security warning count."""
        alerts = tree.findall(f".//alertitem", namespaces)
        return str(len(alerts))
