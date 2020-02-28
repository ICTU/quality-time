"""OWASP ZAP metric collector."""

import re
from datetime import datetime
from typing import cast, Dict, List, Tuple
from xml.etree.ElementTree import Element  # nosec, Element is not available from defusedxml, but only used as type

from dateutil.parser import parse

from collector_utilities.functions import hashless, md5_hash, parse_source_response_xml
from collector_utilities.type import Entities, Entity, Response, Responses, URL, Value
from .source_collector import XMLFileSourceCollector, SourceUpToDatenessCollector


class OWASPZAPSecurityWarnings(XMLFileSourceCollector):
    """Collector to get security warnings from OWASP ZAP."""

    def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        entities: Dict[str, Entity] = {}
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
                uri = self.__stable(hashless(URL(alert_instance.findtext("uri", default=""))))
                key = md5_hash(f"{alert_key}:{method}:{uri}")
                entities[key] = dict(
                    key=key, name=name, description=description, uri=uri, location=f"{method} {uri}", risk=risk)
        return str(len(entities)), "100", list(entities.values())

    def __stable(self, url: URL) -> URL:
        """Return the url without the variable parts."""
        reg_exps = self._parameter("variable_url_regexp")
        stable_url = cast(str, url)
        for reg_exp in reg_exps:
            stable_url = re.sub(reg_exp, "variable-part-removed", stable_url)
        return URL(stable_url)

    @staticmethod
    def __alerts(responses: Responses, risks: List[str]) -> List[Element]:
        """Return a list of the alerts with one of the specified risk levels."""
        alerts = []
        for response in responses:
            tree = parse_source_response_xml(response)
            for risk in risks:
                alerts.extend(tree.findall(f".//alertitem[riskcode='{risk}']"))
        return alerts


class OWASPZAPSourceUpToDateness(XMLFileSourceCollector, SourceUpToDatenessCollector):
    """Collector to collect the OWASP ZAP report age."""

    def _parse_source_response_date_time(self, response: Response) -> datetime:
        return parse(parse_source_response_xml(response).get("generated", ""))
