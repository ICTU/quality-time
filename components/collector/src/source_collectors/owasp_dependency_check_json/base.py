"""Base classes for OWASP Dependency-Check JSON collectors."""

from abc import ABC
from typing import TYPE_CHECKING, ClassVar, cast

from base_collectors import JSONFileSourceCollector
from collector_utilities.exceptions import JSONAttributeError

from .json_types import OWASPDependencyCheckJSON

if TYPE_CHECKING:
    from collector_utilities.type import Response


class OWASPDependencyCheckJSONBase(JSONFileSourceCollector, ABC):
    """Base class for OWASP Dependency-Check JSON collectors."""

    allowed_report_schemas: ClassVar[list[str]] = ["1.1"]

    async def _json(self, response: Response) -> OWASPDependencyCheckJSON:
        """Extract the JSON from the response."""
        json = cast(OWASPDependencyCheckJSON, await response.json(content_type=None))
        self._check_report_schema(json)
        return json

    def _check_report_schema(self, json: OWASPDependencyCheckJSON) -> None:
        """Check that the report schema is allowed."""
        if (schema := json.get("reportSchema", "")) not in self.allowed_report_schemas:
            raise JSONAttributeError(self.allowed_report_schemas, "reportSchema", schema)
