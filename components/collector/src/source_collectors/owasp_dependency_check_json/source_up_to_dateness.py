"""OWASP Dependency-Check JSON source up-to-dateness collector."""

from datetime import datetime
from typing import cast

from base_collectors import TimePassedCollector
from collector_utilities.date_time import parse_datetime
from collector_utilities.type import Response

from .base import OWASPDependencyCheckJSONBase
from .json_types import OWASPDependencyCheckJSON


class OWASPDependencyCheckJSONSourceUpToDateness(OWASPDependencyCheckJSONBase, TimePassedCollector):
    """Collector to collect the OWASP Dependency-Check JSON report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the report date from the JSON."""
        json = cast(OWASPDependencyCheckJSON, await response.json())
        self._check_report_schema(json)
        return parse_datetime(json.get("projectInfo", {}).get("reportDate", ""))
