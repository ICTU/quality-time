"""GitLab collector base classes."""

from abc import ABC
from typing import Dict, Optional, Tuple, Sequence, List, Set

from dateutil.parser import parse

from base_collectors import SourceCollector
from collector_utilities.functions import match_string_or_regular_expression
from collector_utilities.type import URL, Job
from source_model import SourceResponses, SourceMeasurement, Entity


class GitLabBase(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for GitLab collectors."""

    async def _gitlab_api_url(self, api: str) -> URL:
        """Return a GitLab API url with private token, if present in the parameters."""
        url = await super()._api_url()
        project = self._parameter("project", quote=True)
        api_url = f"{url}/api/v4/projects/{project}" + (f"/{api}" if api else "")
        sep = "&" if "?" in api_url else "?"
        api_url += f"{sep}per_page=100"
        return URL(api_url)

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to follow GitLab pagination links, if necessary."""
        responses = await super()._get_source_responses(*urls)
        next_urls = [
            next_url for response in responses if (next_url := response.links.get("next", {}).get("url"))
        ]  # pylint: disable=superfluous-parens
        if next_urls:
            responses.extend(await self._get_source_responses(*next_urls))
        return responses

    def _basic_auth_credentials(self) -> Optional[Tuple[str, str]]:
        """Override to return None, as the private token is passed as header."""
        return None

    def _headers(self) -> Dict[str, str]:
        """Extend to add the private token, if any, to the headers."""
        headers = super()._headers()
        if private_token := self._parameter("private_token"):
            headers["Private-Token"] = str(private_token)
        return headers


class GitLabJobsBase(GitLabBase):
    """Base class for GitLab job collectors."""

    async def _api_url(self) -> URL:
        """Override to return the jobs API."""
        return await self._gitlab_api_url("jobs")

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the jobs from the responses."""
        jobs = await self.__jobs(responses)
        entities = [
            Entity(
                key=job["id"],
                name=job["name"],
                url=job["web_url"],
                build_status=job["status"],
                branch=job["ref"],
                stage=job["stage"],
                build_date=str(parse(job["created_at"]).date()),
            )
            for job in jobs
        ]
        return SourceMeasurement(entities=entities)

    async def __jobs(self, responses: SourceResponses) -> Sequence[Job]:
        """Return the jobs to count."""
        jobs: List[Job] = []
        jobs_seen: Set[Tuple[str, str, str]] = set()
        for response in responses:
            for job in await response.json():
                job_fingerprint = job["name"], job["stage"], job["ref"]
                if job_fingerprint in jobs_seen:
                    continue
                jobs_seen.add(job_fingerprint)
                if self._count_job(job):
                    jobs.append(job)
        return jobs

    def _count_job(self, job: Job) -> bool:
        """Return whether to count the job."""
        return not match_string_or_regular_expression(
            job["name"], self._parameter("jobs_to_ignore")
        ) and not match_string_or_regular_expression(job["ref"], self._parameter("refs_to_ignore"))
