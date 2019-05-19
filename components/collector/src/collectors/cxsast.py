"""Collectors for the Checkmarx CxSAST product."""

from typing import Optional

from dateutil.parser import parse
import requests

from ..collector import Collector
from ..type import URL, Value
from ..util import days_ago


class CxSASTSourceUpToDateness(Collector):
    """Collector class to measure the up-to-dateness of a Checkmarx CxSAST scan."""

    def landing_url(self, response: Optional[requests.Response], **parameters) -> URL:
        project_id = parameters.get("project")
        return URL(f"{self.api_url(**parameters)}/CxWebClient/projectscans.aspx?id={project_id}")

    def get_source_response(self, api_url: URL, **parameters) -> requests.Response:
        """Override because we need to do multiple requests to get all the data we need."""
        # See https://checkmarx.atlassian.net/wiki/spaces/KC/pages/1187774721/Using+the+CxSAST+REST+API+v8.6.0+and+up
        credentials = dict(
            username=parameters.get("username", ""), password=parameters.get("password", ""),
            grant_type="password", scope="sast_rest_api", client_id="resource_owner_client",
            client_secret="014DF517-39D1-4453-B7B3-9930C563627C")
        response = requests.post(
            f"{self.api_url(**parameters)}/cxrestapi/auth/identity/connect/token", data=credentials,
            timeout=self.TIMEOUT, verify=False)
        response.raise_for_status()
        return response

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        token = response.json()['access_token']
        project_id = self.project_id(token, **parameters)
        response = self.open_api(f"sast/scans?projectId={project_id}&scanStatus=Finished&last=1", token, **parameters)
        return str(days_ago(parse(response.json()[0]["dateAndTime"]["finishedOn"])))

    def project_id(self, token: str, **parameters) -> str:
        """Return the project id that belongs to the project parameter."""
        project_name_or_id = parameters.get("project")
        projects = self.open_api(f"projects", token, **parameters).json()
        return [project for project in projects if project_name_or_id in (project["name"], project["id"])][0]["id"]

    def open_api(self, api: str, token: str, **parameters) -> requests.Response:
        """Open the API and return the response."""
        response = requests.get(
            f"{self.api_url(**parameters)}/cxrestapi/{api}", headers=dict(Authorization=f"Bearer {token}"),
            timeout=self.TIMEOUT, verify=False)
        response.raise_for_status()
        return response
