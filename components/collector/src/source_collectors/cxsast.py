"""Collectors for the Checkmarx CxSAST product."""

from abc import ABC
from typing import cast, Dict, Optional, Tuple

from dateutil.parser import parse
import aiohttp

from collector_utilities.type import Entities, Response, Responses, URL, Value
from collector_utilities.functions import days_ago
from .source_collector import SourceCollector


class CxSASTBase(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for CxSAST collectors."""

    def __init__(self, *args, **kwargs) -> None:
        self.__token: Optional[str] = None
        self.__project_id: Optional[str] = None
        self._scan_id: Optional[str] = None
        super().__init__(*args, **kwargs)

    def _headers(self) -> Dict[str, str]:
        headers = super()._headers()
        headers["Authorization"] = f"Bearer {self.__token}"
        return headers

    def _basic_auth_credentials(self) -> Optional[Tuple[str, str]]:
        return None

    async def _landing_url(self, responses: Responses) -> URL:
        api_url = self._api_url()
        return URL(f"{api_url}/CxWebClient/ViewerMain.aspx?scanId={self._scan_id}&ProjectID={self.__project_id}") \
            if responses else api_url

    async def _get_source_responses(self, api_url: URL) -> Responses:
        """Override because we need to do multiple requests to get all the data we need."""
        # See https://checkmarx.atlassian.net/wiki/spaces/KC/pages/1187774721/Using+the+CxSAST+REST+API+v8.6.0+and+up
        credentials = dict(  # nosec, The client secret is not really secret, see previous url
            username=cast(str, self._parameter("username")),
            password=cast(str, self._parameter("password")),
            grant_type="password", scope="sast_rest_api", client_id="resource_owner_client",
            client_secret="014DF517-39D1-4453-B7B3-9930C563627C")
        token_response = await self.__api_post("auth/identity/connect/token", credentials)
        self.__token = (await token_response.json())['access_token']
        project_api = URL(f"{self._api_url()}/cxrestapi/projects")
        project_response = (await super()._get_source_responses(project_api))[0]
        self.__project_id = self.__get_project_id(project_response)
        scan_api = URL(
            f"{self._api_url()}/cxrestapi/sast/scans?projectId={self.__project_id}&scanStatus=Finished&last=1")
        scan_response = (await super()._get_source_responses(scan_api))[0]
        self._scan_id = scan_response.json()[0]["id"]
        return [scan_response]

    def __get_project_id(self, project_response: Response) -> str:
        """Return the project id that belongs to the project parameter."""
        project_name_or_id = self._parameter("project")
        projects = project_response.json()
        return str([project for project in projects if project_name_or_id in (project["name"], project["id"])][0]["id"])

    async def __api_post(self, api: str, data) -> aiohttp.ClientResponse:
        """Post to the API and return the response."""
        timeout = aiohttp.ClientTimeout(self.TIMEOUT)
        response = await self._session.post(f"{self._api_url()}/cxrestapi/{api}", data=data, timeout=timeout)
        response.raise_for_status()
        return response


class CxSASTSourceUpToDateness(CxSASTBase):
    """Collector class to measure the up-to-dateness of a Checkmarx CxSAST scan."""

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        scan = responses[0].json()[0]
        return str(days_ago(parse(scan["dateAndTime"]["finishedOn"]))), "100", []


class CxSASTSecurityWarnings(CxSASTBase):
    """Collector class to measure the number of security warnings in a Checkmarx CxSAST scan."""

    async def _get_source_responses(self, api_url: URL) -> Responses:
        await super()._get_source_responses(api_url)  # Get token
        stats_api = URL(f"{self._api_url()}/cxrestapi/sast/scans/{self._scan_id}/resultsStatistics")
        return await SourceCollector._get_source_responses(self, stats_api)  # pylint: disable=protected-access

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        stats = responses[0].json()
        severities = self._parameter("severities")
        return str(sum(stats.get(f"{severity.lower()}Severity", 0) for severity in severities)), "100", []
