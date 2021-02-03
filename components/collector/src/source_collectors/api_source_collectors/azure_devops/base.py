"""Azure Devops Server base classes for collectors."""

import urllib.parse
from abc import ABC

from base_collectors import SourceCollector
from collector_utilities.type import URL


class AzureDevopsRepositoryBase(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for Azure DevOps collectors that work with repositories."""

    async def _repository_id(self) -> str:
        """Return the repository id belonging to the repository."""
        api_url = str(await super()._api_url())
        repository = self._parameter("repository") or urllib.parse.unquote(api_url.rsplit("/", 1)[-1])
        repositories_url = URL(f"{api_url}/_apis/git/repositories?api-version=4.1")
        repositories = (await (await super()._get_source_responses(repositories_url))[0].json())["value"]
        return str([r for r in repositories if repository in (r["name"], r["id"])][0]["id"])
