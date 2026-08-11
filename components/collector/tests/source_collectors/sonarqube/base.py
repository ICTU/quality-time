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
    def entity(  # noqa: PLR0913, PLR0917
        key: str,
        component: str,
        message: str,
        impacts: str,
        clean_code_attribute_category: str,
        tags: str,
        issue_status: str | None = None,
        rationale: str | None = None,
        creation_date: str | None = None,
        update_date: str | None = None,
        hostname: str = "sonarqube",
    ) -> Entity:
        """Create an entity."""
        entity = Entity(
            key=key,
            component=component,
            message=message,
            impacts=impacts,
            clean_code_attribute_category=clean_code_attribute_category,
            creation_date=creation_date,
            update_date=update_date,
            tags=tags,
            url=f"https://{hostname}/project/issues?id=id&branch=main&issues={key}&open={key}",
        )
        if issue_status is not None:
            entity["issue_status"] = issue_status
        if rationale is not None:
            entity["rationale"] = rationale
        return entity

    @staticmethod
    def sonar_rules(rules_id: str) -> str:
        """Return the SonarQube rules as comma separated string."""
        return ",".join(DATA_MODEL.sources["sonarqube"].configuration[f"{rules_id}_rules"].value)
