"""OWASP Dependency-Check JSON dependencies collector."""

from typing import cast

from collector_utilities.functions import sha1_hash, stabilize
from collector_utilities.type import JSON
from model import Entities, Entity

from .base import OWASPDependencyCheckJSONBase
from .json_types import Dependency, OWASPDependencyCheckJSON


class OWASPDependencyCheckJSONDependencies(OWASPDependencyCheckJSONBase):
    """Collector to get the dependencies from the OWASP Dependency-Check JSON report."""

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the entities from the JSON."""
        owasp_dependency_check_json = cast(OWASPDependencyCheckJSON, json)
        self._check_report_schema(owasp_dependency_check_json)
        landing_url = self._get_landing_url_from_parameters()
        entities = Entities()
        for index, dependency in enumerate(self._dependencies(owasp_dependency_check_json)):
            entities.append(self._parse_entity(dependency, index, landing_url))
        return entities

    def _dependencies(self, owasp_dependency_check_json: OWASPDependencyCheckJSON) -> list[Dependency]:
        """Return the dependencies."""
        return owasp_dependency_check_json.get("dependencies", [])

    def _parse_entity(self, dependency: Dependency, dependency_index: int, landing_url: str) -> Entity:
        """Parse the entity from the dependency."""
        file_path = dependency.get("filePath", "")
        stable_file_path = stabilize(file_path.strip(), cast(list[str], self._parameter("variable_file_path_regexp")))
        file_name = dependency.get("fileName", "")
        sha1 = dependency.get("sha1")
        # We can only generate an entity landing url if a sha1 is present in the JSON, but unfortunately not all
        # dependencies have one, so check for it:
        entity_landing_url = f"{landing_url}#l{dependency_index + 1}_{sha1}" if sha1 else ""
        key = sha1 if sha1 else sha1_hash(stable_file_path + file_name)
        return Entity(
            key=key,
            file_path=file_path,
            file_path_after_regexp=stable_file_path,
            file_name=file_name,
            url=entity_landing_url,
        )
