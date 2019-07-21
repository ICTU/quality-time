"""OWASP ZAP metric collector."""

import re
from typing import List
from xml.etree.ElementTree import Element  # nosec, Element is not available from defusedxml, but only used as type

from dateutil.parser import parse
import requests

from ..source_collectors.source_collector import SourceCollector
from ..utilities.type import Entities, Value
from ..utilities.functions import days_ago, parse_source_response_xml


class OWASPZAPSecurityWarnings(SourceCollector):
    """Collector to get security warnings from OWASP ZAP."""

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str(len(self.alerts(responses)))

    def parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        entities: Entities = []
        tag_re = re.compile(r"<[^>]*>")
        for alert in self.alerts(responses):
            key = ":".join([alert.findtext(id_tag) for id_tag in ("pluginid", "cweid", "wascid", "sourceid")])
            entities.append(
                dict(key=key, name=alert.findtext("name"), description=tag_re.sub("", alert.findtext("desc")),
                     risk=alert.findtext("riskdesc")))
        return entities

    def alerts(self, responses: List[requests.Response]) -> List[Element]:
        """Return a list of the alerts with one of the specified risk levels."""
        tree = parse_source_response_xml(responses[0])
        risks = self.parameters.get("risks") or ["informational", "low", "medium", "high"]
        alerts = []
        for risk in risks:
            risk_code = dict(informational=0, low=1, medium=2, high=3)[risk]
            alerts.extend(tree.findall(f".//alertitem[riskcode='{risk_code}']"))
        return alerts


class OWASPZAPSourceUpToDateness(SourceCollector):
    """Collector to collect the OWASP ZAP report age."""

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        tree = parse_source_response_xml(responses[0])
        report_datetime = parse(tree.get("generated"))
        return str(days_ago(report_datetime))
