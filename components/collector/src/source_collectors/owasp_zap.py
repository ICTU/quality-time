"""OWASP ZAP metric collector."""

import re
from typing import List
from xml.etree.ElementTree import Element  # nosec, Element is not available from defusedxml, but only used as type

from dateutil.parser import parse

from utilities.type import Entities, Responses, URL, Value
from utilities.functions import days_ago, hashless, parse_source_response_xml
from .source_collector import SourceCollector


class OWASPZAPSecurityWarnings(SourceCollector):
    """Collector to get security warnings from OWASP ZAP."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        alert_instances = []
        for alert in self.__alerts(responses):
            alert_instances.extend(alert.findall("./instances/instance"))
        return str(len(alert_instances))

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        entities: Entities = []
        tag_re = re.compile(r"<[^>]*>")
        for alert in self.__alerts(responses):
            alert_key = ":".join(
                [alert.findtext(id_tag, default="") for id_tag in ("pluginid", "cweid", "wascid", "sourceid")])
            name = alert.findtext("name", default="")
            description = tag_re.sub("", alert.findtext("desc", default=""))
            risk = alert.findtext("riskdesc", default="")
            for alert_instance in alert.findall("./instances/instance"):
                method = alert_instance.findtext("method", default="")
                uri = hashless(URL(alert_instance.findtext("uri", default="")))
                key = f"{alert_key}:{method}:{uri}"
                entities.append(
                    dict(key=key, name=name, description=description, uri=uri, location=f"{method} {uri}", risk=risk))
        return entities

    def __alerts(self, responses: Responses) -> List[Element]:
        """Return a list of the alerts with one of the specified risk levels."""
        tree = parse_source_response_xml(responses[0])
        alerts = []
        for risk in self._parameter("risks"):
            risk_code = dict(informational=0, low=1, medium=2, high=3)[risk]
            alerts.extend(tree.findall(f".//alertitem[riskcode='{risk_code}']"))
        return alerts


class OWASPZAPSourceUpToDateness(SourceCollector):
    """Collector to collect the OWASP ZAP report age."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        tree = parse_source_response_xml(responses[0])
        report_datetime = parse(tree.get("generated", ""))
        return str(days_ago(report_datetime))
