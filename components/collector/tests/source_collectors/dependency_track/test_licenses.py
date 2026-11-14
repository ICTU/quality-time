"""Unit tests for the Dependency-Track licenses collector."""

import unittest
from typing import TYPE_CHECKING

from shared_data_model import DATA_MODEL

import source_collectors  # noqa: F401
from base_collectors import SourceCollector

from .base_test import DependencyTrackTestCase

if TYPE_CHECKING:
    from model.measurement import MetricMeasurement


class DependencyTrackLicensesTest(unittest.TestCase):
    """Unit tests for the Dependency-Track licenses collector."""

    def test_licenses_metric_in_data_model(self):
        """Test that the data model has a licenses metric."""
        self.assertIn("licenses", sorted(DATA_MODEL.metrics))

    def test_licenses_collector_registered(self):
        """Test that there is a Dependency-Track collector for the licenses metric."""
        self.assertIsNotNone(SourceCollector.get_subclass("dependency_track", "licenses"))


class DependencyTrackLicensesCollectorTest(DependencyTrackTestCase):
    """Unit tests for collecting the licenses metric from Dependency-Track."""

    METRIC_TYPE = "licenses"

    def license(self, **attributes) -> dict[str, object]:
        """Create a license as returned by the Dependency-Track license API."""
        return {
            "name": "GNU Lesser General Public License v2.1 only",
            "uuid": "license-uuid",
            "licenseId": "LGPL-2.1-only",
            "isOsiApproved": True,
            "isFsfLibre": True,
            "isDeprecatedLicenseId": False,
            "licenseGroups": [{"name": "Weak Copyleft"}, {"name": "Copyleft"}],
        } | attributes

    def licensed_component(self) -> dict[str, object]:
        """Create a component with a resolved license."""
        component = self.component()
        component["resolvedLicense"] = {
            "name": "GNU Lesser General Public License v2.1 only",
            "uuid": "license-uuid",
            "licenseId": "LGPL-2.1-only",
            "licenseText": "The license text is not needed by the collector",
        }
        return component

    def entity(self, **attributes) -> dict[str, str]:
        """Create an expected entity for the licensed component."""
        return {
            "component": "component name",
            "component_landing_url": f"{self.landing_url}/components/component-uuid",
            "component_version": "1.0",
            "key": "component-uuid",
            "license": "GNU Lesser General Public License v2.1 only",
            "license_attributes": "OSI-approved, FSF-Libre",
            "license_groups": "Copyleft, Weak Copyleft",
            "license_id": "LGPL-2.1-only",
            "project": "project name",
            "project_landing_url": f"{self.landing_url}/projects/project uuid",
            "project_version": "1.4",
        } | attributes

    async def collect_components(
        self, components: list[dict[str, object]], licenses: list[dict[str, object]] | None = None
    ) -> MetricMeasurement:
        """Collect a measurement for the given components and licenses."""
        licenses = [self.license()] if licenses is None else licenses
        return await self.collect_measurement(get_request_json_side_effect=[self.projects(), licenses, components])

    async def assert_licensed_component_counted(self, *, counted: bool) -> None:
        """Assert whether the component with the resolved license is counted, given the parameters set."""
        measurement = await self.collect_components([self.licensed_component()])
        if counted:
            self.assert_measurement(measurement, value="1", total="1", entities=[self.entity()])
        else:
            self.assert_measurement(measurement, value="0", total="1", entities=[])

    async def test_no_projects(self):
        """Test that the measurement fails if there are no projects."""
        measurement = await self.collect_measurement(get_request_json_return_value=[])
        self.assert_no_projects_found(measurement)

    async def test_project_without_components(self):
        """Test one project without components."""
        measurement = await self.collect_components([])
        self.assert_measurement(measurement, value="0", entities=[])

    async def test_resolved_license(self):
        """Test that a component with a resolved license gets the name, identifier, groups and attributes."""
        await self.assert_licensed_component_counted(counted=True)

    async def test_resolved_license_not_in_license_list(self):
        """Test that a resolved license that is missing from the license list only gets its name."""
        component = self.component()
        component["resolvedLicense"] = {"name": "Custom license", "uuid": "custom-license-uuid"}
        measurement = await self.collect_components([component])
        expected_entity = self.entity(license="Custom license", license_id="", license_groups="", license_attributes="")
        self.assert_measurement(measurement, value="1", entities=[expected_entity])

    async def test_unresolved_license(self):
        """Test that a component whose license Dependency-Track could not resolve gets the license name only."""
        component = self.component()
        component["license"] = "Some license"
        measurement = await self.collect_components([component])
        expected_entity = self.entity(license="Some license", license_id="", license_groups="", license_attributes="")
        self.assert_measurement(measurement, value="1", entities=[expected_entity])

    async def test_component_without_license(self):
        """Test that a component without license is not counted."""
        component = self.component()
        component["license"] = ""
        measurement = await self.collect_components([component, self.component(name="other", uuid="other-uuid")])
        self.assert_measurement(measurement, value="0", total="0", entities=[])

    async def test_license_without_groups_and_attributes(self):
        """Test that a license without groups and attributes has empty groups and attributes."""
        license_ = self.license(isOsiApproved=False, isFsfLibre=False)
        del license_["licenseGroups"]
        measurement = await self.collect_components([self.licensed_component()], [license_])
        self.assert_measurement(
            measurement, value="1", entities=[self.entity(license_groups="", license_attributes="")]
        )

    async def test_component_without_version(self):
        """Test that a component without version has an empty version."""
        component = self.licensed_component()
        del component["version"]
        measurement = await self.collect_components([component])
        self.assert_measurement(measurement, value="1", entities=[self.entity(component_version="")])

    async def test_components_to_ignore(self):
        """Test that components can be ignored."""
        self.set_source_parameter("components_to_ignore", ["component .*"])
        await self.assert_licensed_component_counted(counted=False)

    async def test_licenses_to_include_by_identifier(self):
        """Test that licenses can be included by SPDX license identifier."""
        self.set_source_parameter("licenses_to_include", ["LGPL-.*"])
        await self.assert_licensed_component_counted(counted=True)

    async def test_licenses_to_include_without_match(self):
        """Test that licenses that don't match the licenses to include are not counted."""
        self.set_source_parameter("licenses_to_include", ["MIT"])
        await self.assert_licensed_component_counted(counted=False)

    async def test_licenses_to_ignore_by_name(self):
        """Test that licenses can be ignored by name."""
        self.set_source_parameter("licenses_to_ignore", ["GNU Lesser .*"])
        await self.assert_licensed_component_counted(counted=False)

    async def test_licenses_to_ignore_without_match(self):
        """Test that licenses that don't match the licenses to ignore are counted."""
        self.set_source_parameter("licenses_to_ignore", ["MIT"])
        await self.assert_licensed_component_counted(counted=True)

    async def test_license_groups_to_include_with_match(self):
        """Test that licenses in one of the license groups to include are counted."""
        self.set_source_parameter("license_groups_to_include", ["Copyleft", "Permissive"])
        await self.assert_licensed_component_counted(counted=True)

    async def test_license_groups_to_include_without_match(self):
        """Test that licenses in none of the license groups to include are not counted."""
        self.set_source_parameter("license_groups_to_include", ["Permissive"])
        await self.assert_licensed_component_counted(counted=False)

    async def test_license_groups_to_ignore_with_match(self):
        """Test that licenses in one of the license groups to ignore are not counted."""
        self.set_source_parameter("license_groups_to_ignore", ["Weak Copyleft"])
        await self.assert_licensed_component_counted(counted=False)

    async def test_license_groups_to_ignore_without_match(self):
        """Test that licenses in none of the license groups to ignore are counted."""
        self.set_source_parameter("license_groups_to_ignore", ["Non-Commercial"])
        await self.assert_licensed_component_counted(counted=True)

    async def test_license_attributes_to_include_with_match(self):
        """Test that licenses with one of the license attributes to include are counted."""
        self.set_source_parameter("license_attributes_to_include", ["OSI-approved"])
        await self.assert_licensed_component_counted(counted=True)

    async def test_license_attributes_to_include_without_match(self):
        """Test that licenses with none of the license attributes to include are not counted."""
        self.set_source_parameter("license_attributes_to_include", ["Deprecated"])
        await self.assert_licensed_component_counted(counted=False)

    async def test_license_attributes_to_ignore_with_match(self):
        """Test that licenses with one of the license attributes to ignore are not counted."""
        self.set_source_parameter("license_attributes_to_ignore", ["FSF-Libre"])
        await self.assert_licensed_component_counted(counted=False)

    async def test_license_attributes_to_ignore_without_match(self):
        """Test that licenses with none of the license attributes to ignore are counted."""
        self.set_source_parameter("license_attributes_to_ignore", ["Deprecated"])
        await self.assert_licensed_component_counted(counted=True)

    async def test_filter_by_latest_project(self):
        """Test that projects can be filtered by being the latest project version."""
        self.set_source_parameter("only_include_latest_project_versions", "yes")
        measurement = await self.collect_measurement(get_request_json_side_effect=[self.projects()])
        self.assert_no_projects_found(measurement)
