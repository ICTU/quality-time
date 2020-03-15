"""Source collector base classes."""

import asyncio
import io
import itertools
import zipfile
from abc import ABC
from typing import cast, Dict, List

from collector_utilities.type import Response, Responses, URL
from .source_collector import FakeResponse, SourceCollector


class FileSourceCollector(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for source collectors that retrieve files."""

    file_extensions: List[str] = []  # Subclass responsibility

    async def _get_source_responses(self, *urls: URL) -> Responses:
        responses = await super()._get_source_responses(*urls)
        if not urls[0].endswith(".zip"):
            return responses
        unzipped_responses = await asyncio.gather(*[self.__unzip(response) for response in responses])
        return list(itertools.chain(*unzipped_responses))

    def _headers(self) -> Dict[str, str]:
        headers = super()._headers()
        if token := cast(str, self._parameter("private_token")):
            # GitLab needs this header, see
            # https://docs.gitlab.com/ee/api/jobs.html#download-a-single-artifact-file-by-job-id
            headers["Private-Token"] = token
        return headers

    @classmethod
    async def __unzip(cls, response: Response) -> Responses:
        """Unzip the response content and return a (new) response for each applicable file in the zip archive."""
        with zipfile.ZipFile(io.BytesIO(await response.read())) as response_zipfile:
            names = [name for name in response_zipfile.namelist() if name.split(".")[-1].lower() in cls.file_extensions]
            responses = [FakeResponse(response_zipfile.read(name)) for name in names]
        return cast(Responses, responses)


class CSVFileSourceCollector(FileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for source collectors that retrieve CSV files."""

    file_extensions = ["csv"]


class HTMLFileSourceCollector(FileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for source collectors that retrieve HTML files."""

    file_extensions = ["html", "htm"]


class JSONFileSourceCollector(FileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for source collectors that retrieve JSON files."""

    file_extensions = ["json"]


class XMLFileSourceCollector(FileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for source collectors that retrieve XML files."""

    file_extensions = ["xml"]
