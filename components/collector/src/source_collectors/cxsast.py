"""Collectors for the Checkmarx CxSAST product."""

from datetime import datetime
from typing import cast, List

from dateutil.parser import parse
from defusedxml import ElementTree
import cachetools
import requests

from utilities.type import Entities, URL, Value
from utilities.functions import days_ago
from .source_collector import SourceCollector


class CxSASTBase(SourceCollector):
    """Base class for CxSAST collectors."""

    TOKEN_RESPONSE, PROJECT_RESPONSE, SCAN_RESPONSE = range(3)

    def landing_url(self, responses: List[requests.Response]) -> URL:
        api_url = self.api_url()
        if len(responses) > self.PROJECT_RESPONSE:
            project_id = self.project_id(responses[self.PROJECT_RESPONSE])
            return URL(f"{api_url}/CxWebClient/projectscans.aspx?id={project_id}")
        return api_url

    def get_source_responses(self, api_url: URL) -> List[requests.Response]:
        """Override because we need to do multiple requests to get all the data we need."""
        # See https://checkmarx.atlassian.net/wiki/spaces/KC/pages/1187774721/Using+the+CxSAST+REST+API+v8.6.0+and+up
        credentials = dict(  # nosec, The client secret is not really secret, see previous url
            username=cast(str, self.parameters.get("username", "")),
            password=cast(str, self.parameters.get("password", "")),
            grant_type="password", scope="sast_rest_api", client_id="resource_owner_client",
            client_secret="014DF517-39D1-4453-B7B3-9930C563627C")
        token_response = self.api_post("auth/identity/connect/token", credentials)
        token = token_response.json()['access_token']
        project_response = self.api_get(f"projects", token)
        project_id = self.project_id(project_response)
        scan_response = self.api_get(f"sast/scans?projectId={project_id}&scanStatus=Finished&last=1", token)
        return [token_response, project_response, scan_response]

    def project_id(self, project_response: requests.Response) -> str:
        """Return the project id that belongs to the project parameter."""
        project_name_or_id = self.parameters.get("project")
        projects = project_response.json()
        return [project for project in projects if project_name_or_id in (project["name"], project["id"])][0]["id"]

    def api_get(self, api: str, token: str) -> requests.Response:
        """Open the API and return the response."""
        response = requests.get(
            f"{self.api_url()}/cxrestapi/{api}", headers=dict(Authorization=f"Bearer {token}"), timeout=self.TIMEOUT)
        response.raise_for_status()
        return response

    def api_post(self, api: str, data, token: str = None) -> requests.Response:
        """Post to the API and return the response."""
        headers = dict(Authorization=f"Bearer {token}") if token else dict()
        response = requests.post(f"{self.api_url()}/cxrestapi/{api}", data=data, headers=headers, timeout=self.TIMEOUT)
        response.raise_for_status()
        return response


class CxSASTSourceUpToDateness(CxSASTBase):
    """Collector class to measure the up-to-dateness of a Checkmarx CxSAST scan."""

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        scan = responses[self.SCAN_RESPONSE].json()[0]
        return str(days_ago(parse(scan["dateAndTime"]["finishedOn"])))


class CxSASTSecurityWarnings(CxSASTBase):
    """Collector class to measure the number of security warnings in a Checkmarx CxSAST scan."""

    CXSAST_SCAN_REPORTS = cachetools.LRUCache(256)  # Mapping of scan ids to scan report ids
    STATS_RESPONSE, XML_REPORT_RESPONSE = range(3, 5)

    def __init__(self, source) -> None:
        super().__init__(source)
        self.report_status = "In Process"

    def get_source_responses(self, api_url: URL) -> List[requests.Response]:
        responses = super().get_source_responses(api_url)
        token = responses[self.TOKEN_RESPONSE].json()["access_token"]
        scan_id = responses[self.SCAN_RESPONSE].json()[0]["id"]
        # Get the statistics of the last scan; this is a single API call:
        responses.append(self.api_get(f"sast/scans/{scan_id}/resultsStatistics", token))
        # We want to get the security warning details. For that, we need to have Checkmarx create an XML report.
        # First, check if we've requested a report in a previous run. If so, we have a report id. If not, request it.
        report_id = self.CXSAST_SCAN_REPORTS.get(scan_id)
        if not report_id:
            response = self.api_post("reports/sastScan", dict(reportType="XML", scanId=scan_id), token)
            report_id = self.CXSAST_SCAN_REPORTS[scan_id] = response.json()["reportId"]
        # Next, get the report status
        response = self.api_get(f"reports/sastScan/{report_id}/status", token)
        self.report_status = response.json()["status"]["value"]
        # Finally, if the report is ready, get it.
        if self.report_status == "Created":
            responses.append(self.api_get(f"reports/sastScan/{report_id}", token))
        return responses

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        stats = responses[self.STATS_RESPONSE].json()
        severities = self.parameters.get("severities") or ["info", "low", "medium", "high"]
        return str(sum([stats.get(f"{severity.lower()}Severity", 0) for severity in severities]))

    def parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        return self.parse_xml_report(responses[self.XML_REPORT_RESPONSE].text) \
            if len(responses) > self.XML_REPORT_RESPONSE else []

    def next_collection(self) -> datetime:
        """If the CxSAST report is in process, try again as soon as possible, otherwise return the regular next
        collection datetime."""
        return datetime.min if self.report_status == "In Process" else super().next_collection()

    def parse_xml_report(self, xml_string: str) -> Entities:
        """Get the entities from the CxSAST XML report."""
        root = ElementTree.fromstring(xml_string)
        severities = self.parameters.get("severities") or ["info", "low", "medium", 'high']
        entities: Entities = []
        for query in root.findall(".//Query"):
            for result in query.findall("Result"):
                severity = result.attrib["Severity"]
                if result.attrib["FalsePositive"] == 'False' and severity.lower() in severities:
                    location = f"{result.attrib['FileName']}:{result.attrib['Line']}:{result.attrib['Column']}"
                    entities.append(dict(key=result.attrib["NodeId"], name=query.attrib["name"],
                                         location=location, severity=severity, url=result.attrib["DeepLink"]))
        return entities
