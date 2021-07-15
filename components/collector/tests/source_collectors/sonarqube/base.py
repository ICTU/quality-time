"""Base classes for SonarQube collector unit tests."""

from model import Entity

from ..source_collector_test_case import SourceCollectorTestCase


class SonarQubeTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for the SonarQube metrics unit tests."""

    SOURCE_TYPE = "sonarqube"

    def setUp(self):
        """Extend to set up the SonarQube source fixture and some URLs."""
        super().setUp()
        self.set_source_parameter("component", "id")
        self.issues_landing_url = "https://sonarqube/project/issues?id=id&resolved=false&branch=master"
        self.metric_landing_url = "https://sonarqube/component_measures?id=id&metric={0}&branch=master"

    @staticmethod
    def entity(  # pylint: disable=too-many-arguments
        key: str,
        component: str,
        entity_type: str,
        message: str,
        severity: str = None,
        resolution: str = None,
        review_priority: str = None,
        creation_date: str = None,
        update_date: str = None,
    ) -> Entity:
        """Create an entity."""
        url = (
            f"https://sonarqube/security_hotspots?id=id&hotspots={key}&branch=master"
            if entity_type == "security_hotspot"
            else f"https://sonarqube/project/issues?id=id&issues={key}&open={key}&branch=master"
        )
        entity = Entity(
            key=key,
            component=component,
            type=entity_type,
            message=message,
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
