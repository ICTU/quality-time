"""OWASP Dependency-Check JSON source up-to-dateness collector."""

from typing import TYPE_CHECKING, cast

from base_collectors import TimePassedCollector
from collector_utilities.date_time import parse_datetime

from .base import OWASPDependencyCheckJSONBase
from .json_types import OWASPDependencyCheckJSON

if TYPE_CHECKING:
    from datetime import datetime

    from collector_utilities.type import Response


class OWASPDependencyCheckJSONSourceUpToDateness(OWASPDependencyCheckJSONBase, TimePassedCollector):
    """Collector to collect the OWASP Dependency-Check JSON report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the report date from the JSON."""
        json = cast(OWASPDependencyCheckJSON, await response.json())
        self._check_report_schema(json)
        return parse_datetime(json.get("projectInfo", {}).get("reportDate", ""))
