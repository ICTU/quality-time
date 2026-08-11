"""Unit tests for the SonarQube source."""

from .base import SonarQubeTestCase


class SonarQubeSecurityWarningsTest(SonarQubeTestCase):
    """Unit tests for the SonarQube security warnings collector."""

    METRIC_TYPE = "security_warnings"
    SONARQUBE_URL = "https://sonarqube"
    API_URL = f"{SONARQUBE_URL}/api"
    BRANCH = "&branch=main"
    ISSUES_API = (
        f"{API_URL}/issues/search?projects=id&branch=main&resolved=false&ps=500&impactSoftwareQualities=SECURITY"
    )
    ISSUES_LANDING_URL = f"{SONARQUBE_URL}/project/issues?id=id{BRANCH}&resolved=false&impactSoftwareQualities=SECURITY"

    def setUp(self):
        """Extend to set up SonarQube security warnings."""
        super().setUp()
        self.issues_json = {
            "total": "3",
            "issues": [
                {
                    "key": "issue1",
                    "message": "message1",
                    "component": "component1",
                    "impacts": [{"severity": "low", "softwareQuality": "security"}],
                    "cleanCodeAttributeCategory": "RESPONSIBLE",
                    "creationDate": "2020-08-30T22:48:52+0200",
                    "updateDate": "2020-09-30T22:48:52+0200",
                    "tags": ["bug"],
                },
                {
                    "key": "issue2",
                    "message": "message2",
                    "component": "component2",
                    "impacts": [{"severity": "medium", "softwareQuality": "security"}],
                    "cleanCodeAttributeCategory": "CONSISTENT",
                    "creationDate": "2019-08-30T22:48:52+0200",
                    "updateDate": "2019-09-30T22:48:52+0200",
                    "tags": ["bug", "injection"],
                },
                {
                    "key": "issue3",
                    "message": "message3",
                    "component": "component3",
                    "impacts": [{"severity": "high", "softwareQuality": "security"}],
                    "cleanCodeAttributeCategory": "CONSISTENT",
                    "creationDate": "2019-08-30T22:48:52+0200",
                    "updateDate": "2019-09-30T22:48:52+0200",
                    "tags": [],
                },
            ],
        }
        self.issue_entities = [
            self.entity(
                key="issue1",
                component="component1",
                message="message1",
                impacts="low impact on security",
                clean_code_attribute_category="responsible",
                creation_date="2020-08-30T22:48:52+0200",
                update_date="2020-09-30T22:48:52+0200",
                tags="bug",
            ),
            self.entity(
                key="issue2",
                component="component2",
                impacts="medium impact on security",
                clean_code_attribute_category="consistent",
                creation_date="2019-08-30T22:48:52+0200",
                update_date="2019-09-30T22:48:52+0200",
                message="message2",
                tags="bug, injection",
            ),
            self.entity(
                key="issue3",
                component="component3",
                impacts="high impact on security",
                clean_code_attribute_category="consistent",
                creation_date="2019-08-30T22:48:52+0200",
                update_date="2019-09-30T22:48:52+0200",
                message="message3",
                tags="",
            ),
        ]

    async def test_security_warnings_vulnerabilities_only(self):
        """Test that issues with security impact are returned."""
        measurement, get, post = await self.collect_measurement_and_mocks(
            get_request_json_return_value=self.issues_json
        )
        get.assert_called_with(self.ISSUES_API, allow_redirects=True, headers={}, auth=None)
        post.assert_not_called()
        self.assert_measurement(
            measurement,
            value="3",
            total="100",
            entities=self.issue_entities,
            landing_url=self.ISSUES_LANDING_URL,
        )

    async def test_filter_security_warning_issues_by_tag(self):
        """Test that the security warning issues can be filtered by tag."""
        self.set_source_parameter("tags", ["injection"])
        measurement, get, post = await self.collect_measurement_and_mocks(
            get_request_json_return_value=self.issues_json
        )
        get.assert_called_with(self.ISSUES_API + "&tags=injection", allow_redirects=True, headers={}, auth=None)
        post.assert_not_called()
        self.assert_measurement(
            measurement,
            value="3",  # SonarQube does the filtering, so here we just get the three entities in self.issues_json
            total="100",
            entities=self.issue_entities,
            landing_url=self.ISSUES_LANDING_URL + "&tags=injection",
        )
