"""Base classes for SonarQube collector unit tests."""

from source_model import Entity

from ...source_collector_test_case import SourceCollectorTestCase


class SonarQubeTestCase(SourceCollectorTestCase):
    """Base class for the SonarQube metrics unit tests."""

    def setUp(self):
        """Extend to set up the SonarQube source fixture and some URLs."""
        super().setUp()
        self.sources = dict(
            source_id=dict(
                type="sonarqube", parameters=dict(url="https://sonar", component="id", types=["bug", "code_smell"])
            )
        )
        self.tests_landing_url = "https://sonar/component_measures?id=id&metric=tests&branch=master"
        self.issues_landing_url = "https://sonar/project/issues?id=id&resolved=false&branch=master"
        self.issue_landing_url = "https://sonar/project/issues?id=id&issues={0}&open={0}&branch=master"
        self.hotspot_landing_url = "https://sonar/security_hotspots?id=id&hotspots={0}&branch=master"
        self.metric_landing_url = "https://sonar/component_measures?id=id&metric={0}&branch=master"

    def entity(  # pylint: disable=too-many-arguments
        self,
        component: str,
        entity_type: str,
        severity: str = None,
        resolution: str = None,
        vulnerability_probability: str = None,
        creation_date: str = None,
        update_date: str = None,
    ) -> Entity:
        """Create an entity."""
        url = (
            self.hotspot_landing_url.format(component)
            if entity_type == "security_hotspot"
            else self.issue_landing_url.format(component)
        )
        entity = Entity(key=component, component=component, message=component, type=entity_type, url=url)
        if severity is not None:
            entity["severity"] = severity
        if resolution is not None:
            entity["resolution"] = resolution
        if vulnerability_probability is not None:
            entity["vulnerability_probability"] = vulnerability_probability
        entity["creation_date"] = creation_date
        entity["update_date"] = update_date
        return entity
