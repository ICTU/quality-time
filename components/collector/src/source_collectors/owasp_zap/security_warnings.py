"""OWASP ZAP security warnings collector."""

import re
from typing import cast
from xml.etree.ElementTree import Element  # nosec, Element is not available from defusedxml, but only used as type

from base_collectors import XMLFileSourceCollector
from collector_utilities.functions import hashless, md5_hash, parse_source_response_xml
from collector_utilities.type import URL
from source_model import Entities, Entity, SourceResponses


class OWASPZAPSecurityWarnings(XMLFileSourceCollector):
    """Collector to get security warnings from OWASP ZAP."""

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the securty warnings from the XML."""
        entities: dict[str, Entity] = {}
        tag_re = re.compile(r"<[^>]*>")
        risks = cast(list[str], self._parameter("risks"))
        for alert in await self.__alerts(responses, risks):
            ids = [
                alert.findtext(id_tag, default="") for id_tag in ("alert", "pluginid", "cweid", "wascid", "sourceid")
            ]
            name = alert.findtext("name", default="")
            description = tag_re.sub("", alert.findtext("desc", default=""))
            risk = alert.findtext("riskdesc", default="")
            for alert_instance in alert.findall("./instances/instance"):
                method = alert_instance.findtext("method", default="")
                uri = self.__stable(hashless(URL(alert_instance.findtext("uri", default=""))))
                key = md5_hash(f"{':'.join(ids)}:{method}:{uri}")
                entities[key] = Entity(
                    key=key,
                    old_key=md5_hash(f"{':'.join(ids[1:])}:{method}:{uri}"),
                    name=name,
                    description=description,
                    uri=uri,
                    location=f"{method} {uri}",
                    risk=risk,
                )
        return list(entities.values())

    def __stable(self, url: URL) -> URL:
        """Return the url without the variable parts."""
        reg_exps = self._parameter("variable_url_regexp")
        stable_url = cast(str, url)
        for reg_exp in reg_exps:
            stable_url = re.sub(reg_exp, "variable-part-removed", stable_url)
        return URL(stable_url)

    @staticmethod
    async def __alerts(responses: SourceResponses, risks: list[str]) -> list[Element]:
        """Return a list of the alerts with one of the specified risk levels."""
        alerts = []
        for response in responses:
            tree = await parse_source_response_xml(response)
            for risk in risks:
                alerts.extend(tree.findall(f".//alertitem[riskcode='{risk}']"))
        return alerts
