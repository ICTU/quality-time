"""OWASP ZAP security warnings collector."""

import re
from typing import cast
from xml.etree.ElementTree import Element  # nosec # Element is not available from defusedxml, but only used as type

from shared.utils.functions import md5_hash

from base_collectors import XMLFileSourceCollector
from collector_utilities.functions import hashless, parse_source_response_xml, stabilize
from collector_utilities.type import URL
from model import Entities, Entity, SourceResponses


class OWASPZAPSecurityWarnings(XMLFileSourceCollector):
    """Collector to get security warnings from OWASP ZAP."""

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the security warnings from the XML."""
        entities: dict[str, Entity] = {}
        tag_re = re.compile(r"<[^>]*>")
        risks = cast(list[str], self._parameter("risks"))
        count_alert_instances = cast(str, self._parameter("alerts")) == "alert instances"
        for alert in await self.__alerts(responses, risks):
            ids = [alert.findtext(id_tag, default="") for id_tag in ("alert", "pluginid", "cweid", "wascid")]
            name = alert.findtext("name", default="")
            description = tag_re.sub("", alert.findtext("desc", default=""))
            risk = alert.findtext("riskdesc", default="")
            entity_kwargs = {"name": name, "description": description, "risk": risk}
            if count_alert_instances:
                for alert_instance in alert.findall("./instances/instance"):
                    entity = self.__alert_instance_entity(ids, entity_kwargs, alert_instance)
                    entities[entity["key"]] = entity
            else:
                entity = self.__alert_type_entity(ids, entity_kwargs)
                entities[entity["key"]] = entity
        return Entities(entities.values())

    def __alert_instance_entity(self, ids: list[str], entity_kwargs: dict[str, str], alert_instance: Element) -> Entity:
        """Create an alert instance entity."""
        method = alert_instance.findtext("method", default="")
        uri = self.__stable_url(hashless(URL(alert_instance.findtext("uri", default=""))))
        key = md5_hash(f"{':'.join(ids)}:{method}:{uri}")
        location = f"{method} {uri}"
        return Entity(key=key, uri=uri, location=location, **entity_kwargs)

    @staticmethod
    def __alert_type_entity(ids: list[str], entity_kwargs: dict[str, str]) -> Entity:
        """Create an alert type entity."""
        return Entity(key=md5_hash(f"{':'.join(ids)}"), **entity_kwargs)

    def __stable_url(self, url: URL) -> URL:
        """Return the url without the variable parts."""
        reg_exps = cast(list[str], self._parameter("variable_url_regexp"))
        return URL(stabilize(url, reg_exps, "variable-part-removed"))

    @staticmethod
    async def __alerts(responses: SourceResponses, risks: list[str]) -> list[Element]:
        """Return a list of the alerts with one of the specified risk levels."""
        alerts = []
        for response in responses:
            tree = await parse_source_response_xml(response)
            for risk in risks:
                alerts.extend(tree.findall(f".//alertitem[riskcode='{risk}']"))
        return alerts
