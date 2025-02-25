"""Checkmarx CxSAST security warnings collector."""

from base_collectors import SourceCollector
from collector_utilities.type import URL, Value
from model import Entities, SourceResponses

from .base import CxSASTScanBase


class CxSASTSecurityWarnings(CxSASTScanBase):
    """Collector class to measure the number of security warnings in a Checkmarx CxSAST scan."""

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to get the scan results."""
        await super()._get_source_responses(*urls)  # Get scan id
        stats_api = URL(f"{await self._api_url()}/cxrestapi/sast/scans/{self._scan_id}/resultsStatistics")
        return await SourceCollector._get_source_responses(self, stats_api)  # noqa: SLF001

    async def _parse_value(self, responses: SourceResponses, included_entities: Entities) -> Value:
        """Override to parse the number of security warnings from the scan results."""
        stats = await responses[0].json()
        severities = self._parameter("severities")
        return str(sum(stats.get(f"{severity.lower()}Severity", 0) for severity in severities))
