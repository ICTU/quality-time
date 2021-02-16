"""Checkmarx CxSAST security warnings collector."""

from base_collectors import SourceCollector
from collector_utilities.type import URL
from source_model import SourceMeasurement, SourceResponses

from .base import CxSASTBase


class CxSASTSecurityWarnings(CxSASTBase):
    """Collector class to measure the number of security warnings in a Checkmarx CxSAST scan."""

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to get the scan results."""
        await super()._get_source_responses(*urls)  # Get token
        stats_api = URL(f"{await self._api_url()}/cxrestapi/sast/scans/{self._scan_id}/resultsStatistics")
        return await SourceCollector._get_source_responses(self, stats_api)  # pylint: disable=protected-access

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the number of security warnings from the scan results."""
        stats = await responses[0].json()
        severities = self._parameter("severities")
        return SourceMeasurement(value=str(sum(stats.get(f"{severity.lower()}Severity", 0) for severity in severities)))
