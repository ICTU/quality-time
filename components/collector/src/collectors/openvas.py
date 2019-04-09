"""OpenVAS metric collector."""

from datetime import datetime, timezone

from dateutil.parser import isoparse  # type: ignore
import requests

from ..collector import Collector
from ..type import Value
from ..util import parse_source_response_xml


class OpenVASSourceUpToDateness(Collector):
    """Collector to collect the OpenVAS report age."""

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        tree, _ = parse_source_response_xml(response)
        report_datetime = isoparse(tree.findtext("creation_time"))
        return str((datetime.now(timezone.utc) - report_datetime).days)
