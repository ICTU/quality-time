"""Checkmarx CxSAST source version collector."""

from packaging.version import Version

from base_collectors import VersionCollector
from collector_utilities.type import URL, Response
from model import SourceResponses

from .base import CxSASTBase


class CxSASTSourceVersion(CxSASTBase, VersionCollector):
    """Collector class to measure the version of a Checkmarx CxSAST source."""

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to get the engine servers."""
        await self._get_token()
        engine_servers_api = URL(f"{await self._api_url()}/cxrestapi/sast/engineServers")
        return await super()._get_source_responses(engine_servers_api)

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Override to get the Checkmarx version from the engine servers info."""
        engine_servers = await response.json()
        return Version(engine_servers[0]["cxVersion"])  # Assume all engine servers have the same Checkmarx version
