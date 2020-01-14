"""OWASP ZAP metric collector."""

import re
from abc import ABC
from datetime import datetime
from typing import cast, List, Tuple
from xml.etree.ElementTree import Element  # nosec, Element is not available from defusedxml, but only used as type

from dateutil.parser import parse

from collector_utilities.functions import hashless, md5_hash, parse_source_response_xml
from collector_utilities.type import Entities, Response, Responses, URL, Value
from .source_collector import FileSourceCollector, SourceUpToDatenessCollector


class OWASPZAPBaseClass(FileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for OWASP ZAP collectors."""

    file_extensions = ["xml"]


class OWASPZAPSecurityWarnings(OWASPZAPBaseClass):
    """Collector to get security warnings from OWASP ZAP."""

    def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        entities: Entities = []
        tag_re = re.compile(r"<[^>]*>")
        risks = cast(List[str], self._parameter("risks"))
        for alert in self.__alerts(responses, risks):
            alert_key = ":".join(
                [alert.findtext(id_tag, default="") for id_tag in ("pluginid", "cweid", "wascid", "sourceid")])
            name = alert.findtext("name", default="")
            description = tag_re.sub("", alert.findtext("desc", default=""))
            risk = alert.findtext("riskdesc", default="")
            for alert_instance in alert.findall("./instances/instance"):
                method = alert_instance.findtext("method", default="")
                uri = hashless(URL(alert_instance.findtext("uri", default="")))
                key = md5_hash(f"{alert_key}:{method}:{uri}")
                entities.append(
                    dict(key=key, name=name, description=description, uri=uri, location=f"{method} {uri}", risk=risk))
        return str(len(entities)), "100", entities

    @staticmethod
    def __alerts(responses: Responses, risks: List[str]) -> List[Element]:
        """Return a list of the alerts with one of the specified risk levels."""
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
