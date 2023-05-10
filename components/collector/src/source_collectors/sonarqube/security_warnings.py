"""SonarQube security warnings collector."""

from base_collectors import SourceCollector
from collector_utilities.type import URL
from model import Entity, SourceMeasurement, SourceResponses

from .base import SonarQubeCollector
from .violations import SonarQubeViolations


class SonarQubeSecurityWarnings(SonarQubeViolations):
    """SonarQube security warnings. The security warnings are a sum of the vulnerabilities and security hotspots."""

    types_parameter = "security_types"

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to return the correct landing url depending on the selected security types."""
        security_types = self._parameter(self.types_parameter)
        base_landing_url = await SourceCollector._landing_url(self, responses)  # pylint: disable=protected-access
        component = self._parameter("component")
        branch = self._parameter("branch")
        common_url_parameters, extra_url_parameters = f"?id={component}&branch={branch}", ""
        if "vulnerability" in security_types and "security_hotspot" in security_types:
            landing_path = "dashboard"
        elif "vulnerability" in security_types:
            landing_path = "project/issues"
            # We don't use self._query_parameter() because when we get here, the value of the types parameter is fixed
            extra_url_parameters = f"{self._query_parameter('severities')}&resolved=false&types=VULNERABILITY"
        else:
            landing_path = "project/security_hotspots"
        return URL(f"{base_landing_url}/{landing_path}{common_url_parameters}{extra_url_parameters}")

    async def _get_source_responses(self, *urls: URL, **kwargs) -> SourceResponses:  # skipcq: PYL-W0613
        """Extend to add urls for the selected security types."""
        api_urls = []
        security_types = self._parameter(self.types_parameter)
        component = self._parameter("component")
        branch = self._parameter("branch")
        base_url = await SonarQubeCollector._api_url(self)  # pylint: disable=protected-access
        if "vulnerability" in security_types:
            api_urls.append(
                URL(
                    f"{base_url}/api/issues/search?componentKeys={component}&resolved=false&ps=500"
                    f"{self._query_parameter('severities')}&branch={branch}&types=VULNERABILITY"
                )
            )
        if "security_hotspot" in security_types:
            api_urls.append(URL(f"{base_url}/api/hotspots/search?projectKey={component}&branch={branch}&ps=500"))
        return await super()._get_source_responses(*api_urls, **kwargs)

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the selected security types."""
        security_types = self._parameter(self.types_parameter)
        vulnerabilities = (
            await super()._parse_source_responses(SourceResponses(responses=[responses[0]]))
            if "vulnerability" in security_types
            else SourceMeasurement()
        )
        if "security_hotspot" in security_types:
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
            entities=vulnerabilities.entities + hotspots,
        )

    def __include_hotspot(self, hotspot) -> bool:
        """Return whether to include the hotspot."""
        review_priorities = self._parameter("review_priorities")
        review_priority = hotspot["vulnerabilityProbability"].lower()
        statuses = self._parameter("hotspot_statuses")
        status = self.__hotspot_status(hotspot)
        return review_priority in review_priorities and status in statuses

    async def __hotspot_entity(self, hotspot) -> Entity:
        """Create the security warning entity for the hotspot."""
        return Entity(
            key=hotspot["key"],
            component=hotspot["component"],
            message=hotspot["message"],
            type="security_hotspot",
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
        url = await SonarQubeCollector._landing_url(self, SourceResponses())  # pylint: disable=protected-access
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(f"{url}/security_hotspots?id={component}&branch={branch}&hotspots={hotspot_key}")
