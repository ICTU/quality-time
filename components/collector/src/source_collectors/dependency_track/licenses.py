"""Dependency-Track licenses collector."""

from typing import TYPE_CHECKING

from model import Entities, Entity, SourceResponses

from .base import DependencyTrackBase

if TYPE_CHECKING:
    from collector_utilities.type import URL

    from .json_types import DependencyTrackComponent, DependencyTrackLicense, DependencyTrackProject


class DependencyTrackLicenses(DependencyTrackBase):
    """Dependency-Track collector for licenses."""

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to get the licenses, and the components with a license, per project.

        The components are processed page by page, keeping only the components that have a license, so that the
        responses for projects with many components don't need to be kept in memory. As the licenses and components
        are kept by the collector, the source responses are empty.
        """
        projects = await self._get_projects_by_uuid()
        self._licenses = await self.__get_licenses()
        self._components: list[tuple[DependencyTrackProject, list[DependencyTrackComponent]]] = []
        for project_uuid, project in projects.items():
            components: list[DependencyTrackComponent] = []
            async for page in self._get_components(project_uuid):
                components.extend(component for component in page if self.__has_license(component))
            self._components.append((project, components))
        return SourceResponses()

    async def __get_licenses(self) -> dict[str, dict[str, str]]:
        """Return the license entity attributes per license UUID, from all pages of the license API."""
        license_api = await self._api_url() / "license"
        licenses = {}
        for response in await super()._get_source_responses(license_api):
            for license_ in await response.json(content_type=None):
                licenses[license_["uuid"]] = self.__license_attributes(license_)
        return licenses

    @staticmethod
    def __has_license(component: DependencyTrackComponent) -> bool:
        """Return whether the component has a license, resolved or not."""
        return "resolvedLicense" in component or bool(component.get("license"))

    @staticmethod
    def __license_attributes(license_: DependencyTrackLicense) -> dict[str, str]:
        """Return the entity attributes of the license."""
        groups = sorted(group["name"] for group in license_.get("licenseGroups", []))
        attributes = {
            "OSI-approved": license_.get("isOsiApproved", False),
            "FSF-Libre": license_.get("isFsfLibre", False),
            "Deprecated": license_.get("isDeprecatedLicenseId", False),
        }
        return {
            "license": license_["name"],
            "license_id": license_.get("licenseId", ""),
            "license_groups": ", ".join(groups),
            "license_attributes": ", ".join(
                attribute for attribute, has_attribute in attributes.items() if has_attribute
            ),
        }

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Parse the entities from the components."""
        entities = Entities()
        for project, components in self._components:
            entities.extend([self._create_entity(component, project) for component in components])
        return entities

    def _create_entity(self, component: DependencyTrackComponent, project: DependencyTrackProject) -> Entity:
        """Create an entity from the component."""
        return Entity(
            component=component["name"],
            component_landing_url=self._landing_url_of_component(component["uuid"]),
            component_version=component.get("version", ""),
            key=component["uuid"],
            project=project["name"],
            project_landing_url=self._landing_url_of_project(project["uuid"]),
            project_version=project.get("version", ""),
            **self.__license(component),
        )

    def __license(self, component: DependencyTrackComponent) -> dict[str, str]:
        """Return the license entity attributes of the component."""
        if resolved_license := component.get("resolvedLicense"):
            if license_attributes := self._licenses.get(resolved_license["uuid"]):
                return license_attributes
            name, license_id = resolved_license["name"], resolved_license.get("licenseId", "")
        else:
            name, license_id = component.get("license", ""), ""
        return {"license": name, "license_id": license_id, "license_groups": "", "license_attributes": ""}

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include the entity in the measurement."""
        return (
            self._matches_filter(entity["component"], "components_to_include", "components_to_ignore")
            and self.__license_matches(entity)
            and self.__matches_choices(
                entity["license_groups"], "license_groups_to_include", "license_groups_to_ignore"
            )
            and self.__matches_choices(
                entity["license_attributes"], "license_attributes_to_include", "license_attributes_to_ignore"
            )
        )

    def __license_matches(self, entity: Entity) -> bool:
        """Return whether the license name or SPDX identifier matches the licenses to include and ignore."""
        names = [name for name in (entity["license"], entity["license_id"]) if name]
        included = any(self._matches_filter(name, "licenses_to_include") for name in names)
        ignored = any(not self._matches_filter(name, exclude_parameter="licenses_to_ignore") for name in names)
        return included and not ignored

    def __matches_choices(self, values: str, include_parameter: str, exclude_parameter: str) -> bool:
        """Return whether the comma separated values match the include and exclude multiple choice parameters."""
        value_set = set(values.split(", ")) if values else set()
        include, exclude = set(self._parameter(include_parameter)), set(self._parameter(exclude_parameter))
        return (not include or bool(include & value_set)) and not exclude & value_set
