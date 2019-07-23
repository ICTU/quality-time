"""OWASP ZAP metric collector."""

import re
from typing import List
from xml.etree.ElementTree import Element  # nosec, Element is not available from defusedxml, but only used as type

from dateutil.parser import parse
import requests

from utilities.type import Entities, Value
from utilities.functions import days_ago, parse_source_response_xml
from .source_collector import SourceCollector


class OWASPZAPSecurityWarnings(SourceCollector):
    """Collector to get security warnings from OWASP ZAP."""

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        alert_instances = []
        for alert in self.alerts(responses):
            alert_instances.extend(alert.findall("./instances/instance"))
        return str(len(alert_instances))

    def parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        entities: Entities = []
        tag_re = re.compile(r"<[^>]*>")
        for alert in self.alerts(responses):
            alert_key = ":".join([alert.findtext(id_tag) for id_tag in ("pluginid", "cweid", "wascid", "sourceid")])
            name = alert.findtext("name")
            description = tag_re.sub("", alert.findtext("desc"))
            risk = alert.findtext("riskdesc")
            for alert_instance in alert.findall("./instances/instance"):
                method = alert_instance.findtext("method")
                uri = alert_instance.findtext("uri")
                key = f"{alert_key}:{method}:{uri}"
                entities.append(
                    dict(key=key, name=name, description=description, uri=uri, location=f"{method} {uri}", risk=risk))
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
