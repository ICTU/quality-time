"""Base classes for SonarQube collector unit tests."""

from shared_data_model import DATA_MODEL

from model import Entity

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class SonarQubeTestCase(SourceCollectorTestCase):
    """Base class for the SonarQube metrics unit tests."""

    SOURCE_TYPE = "sonarqube"

    def setUp(self):
        """Extend to set up the SonarQube source fixture and some URLs."""
        super().setUp()
        self.set_source_parameter("component", "id")
        self.issues_landing_url = "https://sonarqube/project/issues?id=id&branch=main&resolved=false"
        self.metric_landing_url = "https://sonarqube/component_measures?id=id&branch=main&metric={0}"

    @staticmethod
    def entity(  # noqa: PLR0913
        key: str,
        component: str,
        entity_type: str,
        message: str,
        severity: str | None = None,
        resolution: str | None = None,
        rationale: str | None = None,
        review_priority: str | None = None,
        creation_date: str | None = None,
        update_date: str | None = None,
        hotspot_status: str | None = None,
        tags: str | None = None,
    ) -> Entity:
        """Create an entity."""
        url = (
            f"https://sonarqube/security_hotspots?id=id&branch=main&hotspots={key}"
            if entity_type == "security_hotspot"
            else f"https://sonarqube/project/issues?id=id&branch=main&issues={key}&open={key}"
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
        if rationale is not None:
            entity["rationale"] = rationale
        if review_priority is not None:
            entity["review_priority"] = review_priority
        if hotspot_status is not None:
            entity["hotspot_status"] = hotspot_status
        if tags is not None:
            entity["tags"] = tags
        return entity

    @staticmethod
    def sonar_rules(rules_id: str) -> str:
        """Return the SonarQube rules as comma separated string."""
        return ",".join(DATA_MODEL.sources["sonarqube"].configuration[f"{rules_id}_rules"].value)
