"""GitLab collector base classes."""

from abc import ABC
from collections.abc import Sequence
from typing import Optional

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
        all_responses = responses = await super()._get_source_responses(*urls)
        while next_urls := self.__next_urls(responses):
            all_responses.extend(responses := await super()._get_source_responses(*next_urls))
        return all_responses

    def _basic_auth_credentials(self) -> Optional[tuple[str, str]]:
        """Override to return None, as the private token is passed as header."""
        return None

    def _headers(self) -> dict[str, str]:
        """Extend to add the private token, if any, to the headers."""
        headers = super()._headers()
        if private_token := self._parameter("private_token"):
            headers["Private-Token"] = str(private_token)
        return headers

    @staticmethod
    def __next_urls(responses: SourceResponses) -> list[URL]:
        """Return the next (pagination) links from the responses."""
        return [URL(next_url) for response in responses if (next_url := response.links.get("next", {}).get("url"))]


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
        jobs: list[Job] = []
        jobs_seen: set[tuple[str, str, str]] = set()
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
