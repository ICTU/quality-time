"""SonarQube security warnings collector."""

from base_collectors import SourceCollector
from collector_utilities.type import URL
from model import Entity, SourceMeasurement, SourceResponses

from .base import SonarQubeCollector
from .violations import SonarQubeViolations


class SonarQubeSecurityWarnings(SonarQubeViolations):
    """SonarQube security warnings, which are a combination of issues with security impact and security hotspots."""

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to return the correct landing url depending on the selected security types."""
        base_landing_url = await SourceCollector._landing_url(self, responses)  # noqa: SLF001
        component = self._parameter("component")
        branch = self._parameter("branch")
        common_url_parameters, extra_url_parameters = f"?id={component}&branch={branch}", ""
        if self.__issues_with_security_impact_selected() and self.__security_hotspots_selected():
            landing_path = "dashboard"
        elif self.__issues_with_security_impact_selected():
            landing_path = "project/issues"
            extra_url_parameters = f"&resolved=false{self._url_parameters()}"
        else:
            landing_path = "security_hotspots"
        return URL(f"{base_landing_url}/{landing_path}{common_url_parameters}{extra_url_parameters}")

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to add urls for the selected security types."""
        api_urls = []
        component = self._parameter("component")
        branch = self._parameter("branch")
        if self.__issues_with_security_impact_selected():
            api_urls.append(await super()._api_url())
        if self.__security_hotspots_selected():
            base_url = await SonarQubeCollector._api_url(self)  # noqa: SLF001
            # Note we pass both the project and the deprecated projectKey parameter because Sonarcloud.io doesn't
            # accept the project parameter. Tested October 8, 2025.
            api_urls.append(
                URL(
                    f"{base_url}/api/hotspots/search?project={component}&projectKey={component}&branch={branch}&"
                    f"ps={self.PAGE_SIZE}"
                )
            )
        return await super()._get_source_responses(*api_urls)

    def _url_parameters(self) -> str:
        """Override to return parameters needed for issues with security impact, common to API URL and landing URL."""
        return (
            self._query_parameter("impact_severities", uppercase=True)
            + "&impactSoftwareQualities=SECURITY"
            + self._query_parameter("tags")
        )

    async def _entity(self, issue) -> Entity:
        """Extend to set the entity security type."""
        entity = await super()._entity(issue)
        entity["security_type"] = "issue with security impact"
        return entity

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the selected security types."""
        vulnerabilities = (
            await super()._parse_source_responses(SourceResponses(responses=[responses[0]]))
            if self.__issues_with_security_impact_selected()
            else SourceMeasurement()
        )
        if self.__security_hotspots_selected():
            json = await responses[-1].json()
            hotspots = [
                await self.__hotspot_entity(hotspot)
                for hotspot in json.get("hotspots", [])
                if self.__include_hotspot(hotspot)
            ]
        else:
            hotspots = []
        return SourceMeasurement(
            value=str(int(vulnerabilities.value or 0) + len(hotspots)),
            entities=vulnerabilities.get_entities() + hotspots,
        )

    def __include_hotspot(self, hotspot: dict[str, str]) -> bool:
        """Return whether to include the hotspot."""
        review_priorities = self._parameter("review_priorities")
        review_priority = hotspot["vulnerabilityProbability"].lower()
        statuses = self._parameter("hotspot_statuses")
        status = self.__hotspot_status(hotspot)
        return review_priority in review_priorities and status in statuses

    async def __hotspot_entity(self, hotspot: dict[str, str]) -> Entity:
        """Create the security warning entity for the hotspot."""
        return Entity(
            key=hotspot["key"],
            component=hotspot["component"],
            message=hotspot["message"],
            security_type="security hotspot",
            url=await self.__hotspot_landing_url(hotspot["key"]),
            review_priority=hotspot["vulnerabilityProbability"].lower(),
            creation_date=hotspot["creationDate"],
            update_date=hotspot["updateDate"],
            hotspot_status=self.__hotspot_status(hotspot),
        )

    @staticmethod
    def __hotspot_status(hotspot: dict[str, str]) -> str:
        """Return the hotspot status."""
        # The SonarQube documentation describes the hotspot lifecycle as having four statuses (see
        # https://docs.sonarqube.org/latest/user-guide/security-hotspots/#lifecycle): 'to review', 'acknowledged',
        # 'fixed', and 'safe'. However, in the API the status is either 'to review' or 'reviewed' and the other
        # statuses ('acknowledged', 'fixed', and 'safe') are called resolutions. So to determine the status as defined
        # by the docs, check both the hotspot status and the hotspot resolution:
        return "to review" if hotspot["status"] == "TO_REVIEW" else hotspot["resolution"].lower()

    async def __hotspot_landing_url(self, hotspot_key: str) -> URL:
        """Generate a landing url for the hotspot."""
        url = await SonarQubeCollector._landing_url(self, SourceResponses())  # noqa: SLF001
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(f"{url}/security_hotspots?id={component}&branch={branch}&hotspots={hotspot_key}")

    def __issues_with_security_impact_selected(self) -> bool:
        """Return whether the user selected issues with security impact."""
        return "issue with security impact" in self._parameter("security_types")

    def __security_hotspots_selected(self) -> bool:
        """Return whether the user selected security hotspots."""
        return "security hotspot" in self._parameter("security_types")
