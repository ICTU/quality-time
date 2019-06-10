"""OWASP ZAP metric collector."""

import re
from typing import List
from xml.etree.cElementTree import Element

from dateutil.parser import parse
import requests

from ..collector import Collector
from ..type import Entities, Parameter, Value
from ..util import days_ago, parse_source_response_xml


class OWASPZAPSecurityWarnings(Collector):
    """Collector to get security warnings from OWASP ZAP."""

    def parse_source_responses_value(self, responses: List[requests.Response], **parameters: Parameter) -> Value:
        return str(len(self.alerts(responses, **parameters)))

    def parse_source_responses_entities(self, responses: List[requests.Response], **parameters: Parameter) -> Entities:
        entities = []
        tag_re = re.compile(r"<[^>]*>")
        for alert in self.alerts(responses, **parameters):
            key = ":".join([alert.findtext(id_tag) for id_tag in ("pluginid", "cweid", "wascid", "sourceid")])
            entities.append(
                dict(key=key, name=alert.findtext("name"), description=tag_re.sub("", alert.findtext("desc")),
                     risk=alert.findtext("riskdesc")))
        return entities

    @staticmethod
    def alerts(responses: List[requests.Response], **parameters: Parameter) -> List[Element]:
        """Return a list of the alerts with one of the specified risk levels."""
        tree = parse_source_response_xml(responses[0])
        risks = parameters.get("risks") or ["informational", "low", "medium", "high"]
        alerts = []
        for risk in risks:
            risk_code = dict(informational=0, low=1, medium=2, high=3)[risk]
            alerts.extend(tree.findall(f".//alertitem[riskcode='{risk_code}']"))
        return alerts


class OWASPZAPSourceUpToDateness(Collector):
    """Collector to collect the OWASP ZAP report age."""

    def parse_source_responses_value(self, responses: List[requests.Response], **parameters: Parameter) -> Value:
        tree = parse_source_response_xml(responses[0])
        report_datetime = parse(tree.get("generated"))
        return str(days_ago(report_datetime))
