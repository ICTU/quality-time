"""Anchore Jenkins plugin security warnings collector."""

from shared.utils.functions import md5_hash

from base_collectors import SecurityWarningsSourceCollector
from collector_utilities.type import URL
from model import Entities, Entity, SourceResponses


class AnchoreJenkinsPluginSecurityWarnings(SecurityWarningsSourceCollector):
    """Anchore Jenkins plugin security warnings collector."""

    TAG, CVE, SEVERITY, PACKAGE, FIX, CVE_URL = range(6)  # Column indices

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Override to return the URL for the plugin."""
        return URL(f"{await self._api_url()}/lastSuccessfulBuild/anchore-results")

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to get the Anchore security report JSON from the last successful build."""
        # We need to collect the build number of the last successful build because the Anchore Jenkins plugin uses
        # the build number in the name of the folder where it stores the security warnings:
        api_url = await self._api_url()
        responses = await super()._get_source_responses(URL(f"{api_url}/api/json"))
        json = await responses[0].json()
        build = json["lastSuccessfulBuild"]["number"]
        job = json["name"]
        anchore_security_json_url = URL(f"{api_url}/{build}/artifact/AnchoreReport.{job}_{build}/anchore_security.json")
        return await super()._get_source_responses(anchore_security_json_url)

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the Anchore Jenkins plugin security warnings."""
        entities = Entities()
        for response in responses:
            json = await response.json(content_type=None)
            entities.extend([self._create_entity(vulnerability) for vulnerability in json.get("data", [])])
        return entities

    def _create_entity(self, vulnerability: list[str]) -> Entity:
        """Create an entity from the vulnerability."""
        return Entity(
            key=md5_hash(f"{vulnerability[self.TAG]}:{vulnerability[self.CVE]}:{vulnerability[self.PACKAGE]}"),
            tag=vulnerability[self.TAG],
            cve=vulnerability[self.CVE],
            package=vulnerability[self.PACKAGE],
            severity=vulnerability[self.SEVERITY],
            fix=vulnerability[self.FIX],
            url=vulnerability[self.CVE_URL],
        )
