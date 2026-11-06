"""Base classes for Dependency-Track collector unit tests."""

import json
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

from source_collectors.dependency_track.json_types import DependencyTrackMetrics, DependencyTrackProject

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase

if TYPE_CHECKING:
    from collections.abc import Callable

    from model.measurement import MetricMeasurement


class StreamReaderStub:
    """Stub for the aiohttp stream reader, to be able to stream the response content."""

    def __init__(self, content: bytes) -> None:
        self.content = content

    async def read(self, size: int = -1) -> bytes:
        """Return at most size bytes of the content, or all remaining content if size is negative."""
        size = len(self.content) if size < 0 else size
        chunk, self.content = self.content[:size], self.content[size:]
        return chunk


class DependencyTrackTestCase(SourceCollectorTestCase):
    """Base class for Dependency-Track collector unit tests."""

    SOURCE_TYPE = "dependency_track"

    async def collect(self, **kwargs):
        """Extend to give each response its own JSON, so the collector can either read or stream the response."""
        if "get_request_side_effect" not in kwargs:
            kwargs["get_request_side_effect"] = self.__get_responses(
                kwargs.pop("get_request_json_return_value", None),
                kwargs.pop("get_request_json_side_effect", None),
                kwargs.pop("get_request_headers", None),
            )
        return await super().collect(**kwargs)

    @staticmethod
    def __get_responses(json_return_value, json_side_effect, headers) -> Callable[..., AsyncMock]:
        """Return a get request side effect that creates a response for each request."""
        json_items = iter(json_side_effect or [])

        def get_response(*args, **kwargs) -> AsyncMock:  # noqa: ARG001
            """Return a response with the next JSON item, if there are multiple, as JSON and as streamable content."""
            json_item = json_return_value if json_side_effect is None else next(json_items)
            response = AsyncMock()
            response.json.return_value = json_item
            response.content = StreamReaderStub(json.dumps(json_item).encode())
            response.headers = headers or {}
            return response

        return get_response

    def setUp(self) -> None:
        """Extend to add the mandatory landing URL."""
        super().setUp()
        self.landing_url = f"https://{self.SOURCE_TYPE}/landing"
        self.sources["source_id"]["parameters"]["landing_url"] = self.landing_url

    def projects(self, version: str = "1.4", *, is_latest: bool = False) -> list[DependencyTrackProject]:
        """Create the Dependency-Track projects fixture."""
        project = DependencyTrackProject(
            isLatest=is_latest,
            name="project name",
            uuid="project uuid",
            lastBomImport=0,
            metrics=DependencyTrackMetrics(),
        )
        if version:
            project["version"] = version
        return [project]

    def component(
        self,
        name: str = "component name",
        uuid: str = "component-uuid",
        direct_dependencies: list[str] | None = None,
        project: DependencyTrackProject | dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Create a Dependency-Track component fixture, with the UUIDs of its direct dependencies, if any."""
        component: dict[str, object] = {
            "name": name,
            "project": self.projects()[0] if project is None else project,  # Dependency-Track includes the project
            "uuid": uuid,
            "version": "1.0",
        }
        if direct_dependencies is not None:
            component["directDependencies"] = json.dumps([{"uuid": child} for child in direct_dependencies])
        return component

    def root_component_attributes(self, name: str, uuid: str = "") -> dict[str, str]:
        """Create the expected root component entity attributes. Pass the UUID if a landing URL is expected."""
        attributes = {"root_component": name}
        if uuid:
            attributes["root_component_landing_url"] = f"{self.landing_url}/components/{uuid}"
        return attributes

    def assert_no_projects_found(self, measurement: MetricMeasurement) -> None:
        """Assert that no projects have been found."""
        self.assert_measurement(measurement, connection_error="No projects found")
