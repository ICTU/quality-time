"""Base classes for SonarQube collector unit tests."""

from source_model import Entity

from ...source_collector_test_case import SourceCollectorTestCase


class SonarQubeTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for the SonarQube metrics unit tests."""

    def setUp(self):
        """Extend to set up the SonarQube source fixture and some URLs."""
        super().setUp()
        self.sources = dict(
            source_id=dict(
                type="sonarqube", parameters=dict(url="https://sonar", component="id", types=["bug", "code_smell"])
            )
        )
        self.issues_landing_url = "https://sonar/project/issues?id=id&resolved=false&branch=master"
        self.metric_landing_url = "https://sonar/component_measures?id=id&metric={0}&branch=master"

    @staticmethod
    def entity(  # pylint: disable=too-many-arguments
        component: str,
        entity_type: str,
        severity: str = None,
        resolution: str = None,
        review_priority: str = None,
        creation_date: str = None,
        update_date: str = None,
    ) -> Entity:
        """Create an entity."""
        url = (
            f"https://sonar/security_hotspots?id=id&hotspots={component}&branch=master"
            if entity_type == "security_hotspot"
            else f"https://sonar/project/issues?id=id&issues={component}&open={component}&branch=master"
        )
        entity = Entity(
            key=component,
            component=component,
            message=component,
            type=entity_type,
            url=url,
            creation_date=creation_date,
            update_date=update_date,
        )
        if severity is not None:
            entity["severity"] = severity
        if resolution is not None:
            entity["resolution"] = resolution
        if review_priority is not None:
            entity["review_priority"] = review_priority
        return entity
