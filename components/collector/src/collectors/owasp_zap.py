"""OWASP ZAP metric collector."""

from datetime import datetime
import re
from typing import List
from xml.etree.cElementTree import Element

from dateutil.parser import parse
import requests

from ..collector import Collector
from ..type import Units, Value
from ..util import parse_source_response_xml


class OWASPZAPSecurityWarnings(Collector):
    """Collector to get security warnings from OWASP ZAP."""

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        return str(len(self.alerts(response, **parameters)))

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        units = []
        tag_re = re.compile(r"<[^>]*>")
        for alert in self.alerts(response, **parameters):
            key = ":".join([alert.findtext(id_tag) for id_tag in ("pluginid", "cweid", "wascid", "sourceid")])
            units.append(
                dict(key=key, name=alert.findtext("name"), description=tag_re.sub("", alert.findtext("desc")),
                     risk=alert.findtext("riskdesc")))
        return units

    @staticmethod
    def alerts(response: requests.Response, **parameters) -> List[Element]:
        """Return a list of the alerts with one of the specified risk levels."""
        tree, _ = parse_source_response_xml(response)
        risks = parameters.get("risks") or ["informational", "low", "medium", "high"]
        alerts = []
        for risk in risks:
            risk_code = dict(informational=0, low=1, medium=2, high=3)[risk]
            alerts.extend(tree.findall(f".//alertitem[riskcode='{risk_code}']"))
        return alerts


class OWASPZAPSourceFreshness(Collector):
    """Collector to collect the OWASP ZAP report age."""

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        tree, _ = parse_source_response_xml(response)
        report_datetime = parse(tree.get("generated"))
        return str((datetime.now() - report_datetime).days)
