"""OWASP ZAP metric collector."""

import re
from abc import ABC
from datetime import datetime
from typing import List
from xml.etree.ElementTree import Element  # nosec, Element is not available from defusedxml, but only used as type

from dateutil.parser import parse

from collector_utilities.type import Entities, Response, Responses, URL, Value
from collector_utilities.functions import hashless, parse_source_response_xml
from .source_collector import FileSourceCollector, SourceUpToDatenessCollector


class OWASPZAPBaseClass(FileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for OWASP ZAP collectors."""

    file_extensions = ["xml"]


class OWASPZAPSecurityWarnings(OWASPZAPBaseClass):
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
        risks = self._parameter("risks")
        alerts = []
        for response in responses:
            tree = parse_source_response_xml(response)
            for risk in risks:
                alerts.extend(tree.findall(f".//alertitem[riskcode='{risk}']"))
        return alerts


class OWASPZAPSourceUpToDateness(OWASPZAPBaseClass, SourceUpToDatenessCollector):
    """Collector to collect the OWASP ZAP report age."""

    def _parse_source_response_date_time(self, response: Response) -> datetime:
        return parse(parse_source_response_xml(response).get("generated", ""))
