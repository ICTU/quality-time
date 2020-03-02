"""Collectors for the Checkmarx CxSAST product."""

from abc import ABC
from typing import cast, Final, Tuple

from dateutil.parser import parse
import aiohttp
import requests

from collector_utilities.type import Entities, Response, Responses, URL, Value
from collector_utilities.functions import days_ago
from .source_collector import SourceCollector


class CxSASTBase(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for CxSAST collectors."""

    TOKEN_RESPONSE: Final[int] = 0
    PROJECT_RESPONSE: Final[int] = 1
    SCAN_RESPONSE: Final[int] = 2

    def __init__(self, *args, **kwargs) -> None:
        self.__token = None
        super().__init__(*args, **kwargs)

    def _headers(self):
        return dict(Authorization=f"Bearer {self.__token}") if self.__token else {}

    def _landing_url(self, responses: Responses) -> URL:
        api_url = self._api_url()
        if len(responses) > self.SCAN_RESPONSE:
            project_id = self.__project_id(responses[self.PROJECT_RESPONSE])
            scan_id = self._scan_id(responses)
            return URL(f"{api_url}/CxWebClient/ViewerMain.aspx?scanId={scan_id}&ProjectID={project_id}")
        return api_url

    async def _get_source_responses(self, session: aiohttp.ClientSession, api_url: URL) -> Responses:
        """Override because we need to do multiple requests to get all the data we need."""
        # See https://checkmarx.atlassian.net/wiki/spaces/KC/pages/1187774721/Using+the+CxSAST+REST+API+v8.6.0+and+up
        credentials = dict(  # nosec, The client secret is not really secret, see previous url
            username=cast(str, self._parameter("username")),
            password=cast(str, self._parameter("password")),
            grant_type="password", scope="sast_rest_api", client_id="resource_owner_client",
            client_secret="014DF517-39D1-4453-B7B3-9930C563627C")
        token_response = self._api_post("auth/identity/connect/token", credentials)
        self.__token = token_response.json()['access_token']
        project_api = URL(f"{self._api_url()}/cxrestapi/projects")
        project_response = (await super()._get_source_responses(session, project_api))[0]
        project_id = self.__project_id(project_response)
        scan_api = URL(f"{self._api_url()}/cxrestapi/sast/scans?projectId={project_id}&scanStatus=Finished&last=1")
        scan_response = (await super()._get_source_responses(session, scan_api))[0]
        return [token_response, project_response, scan_response]

    def __project_id(self, project_response: Response) -> str:
        """Return the project id that belongs to the project parameter."""
        project_name_or_id = self._parameter("project")
        projects = project_response.json()
        return str([project for project in projects if project_name_or_id in (project["name"], project["id"])][0]["id"])

    def _scan_id(self, responses: Responses) -> str:
        """Return the scan id."""
        return str(responses[self.SCAN_RESPONSE].json()[0]["id"])

    def _api_post(self, api: str, data, token: str = None) -> Response:
        """Post to the API and return the response."""
        headers = dict(Authorization=f"Bearer {token}") if token else dict()
        response = requests.post(f"{self._api_url()}/cxrestapi/{api}", data=data, headers=headers, timeout=self.TIMEOUT)
        response.raise_for_status()
        return response


class CxSASTSourceUpToDateness(CxSASTBase):
    """Collector class to measure the up-to-dateness of a Checkmarx CxSAST scan."""

    def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        scan = responses[self.SCAN_RESPONSE].json()[0]
        return str(days_ago(parse(scan["dateAndTime"]["finishedOn"]))), "100", []


class CxSASTSecurityWarnings(CxSASTBase):
    """Collector class to measure the number of security warnings in a Checkmarx CxSAST scan."""

    STATS_RESPONSE = 3

    async def _get_source_responses(self, session: aiohttp.ClientSession, api_url: URL) -> Responses:
        responses = await super()._get_source_responses(session, api_url)
        scan_id = self._scan_id(responses)
        stats_api = URL(f"{self._api_url()}/cxrestapi/sast/scan/{scan_id}/resultsStatistics")
        return responses + \
            await SourceCollector._get_source_responses(self, session, stats_api)  # pylint: disable=protected-access

    def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        stats = responses[self.STATS_RESPONSE].json()
        severities = self._parameter("severities")
        return str(sum(stats.get(f"{severity.lower()}Severity", 0) for severity in severities)), "100", []
