"""Unit tests for the SonarQube source."""

from .base import SonarQubeTestCase


class SonarQubeSecurityWarningsTest(SonarQubeTestCase):
    """Unit tests for the SonarQube security warnings collector."""

    METRIC_TYPE = "security_warnings"

    def setUp(self):
        """Extend to set up SonarQube security warnings."""
        super().setUp()
        self.vulnerabilities_json = dict(
            total="2",
            issues=[
                dict(
                    key="vulnerability1",
                    message="message1",
                    component="component1",
                    severity="INFO",
                    type="VULNERABILITY",
                    creationDate="2020-08-30T22:48:52+0200",
                    updateDate="2020-09-30T22:48:52+0200",
                ),
                dict(
                    key="vulnerability2",
                    message="message2",
                    component="component2",
                    severity="MAJOR",
                    type="VULNERABILITY",
                    creationDate="2019-08-30T22:48:52+0200",
                    updateDate="2019-09-30T22:48:52+0200",
                ),
            ],
        )
        self.hotspots_json = dict(
            paging=dict(total="2"),
            hotspots=[
                dict(
                    key="hotspot1",
                    message="message1",
                    component="component1",
                    vulnerabilityProbability="MEDIUM",
                    creationDate="2010-12-13T10:37:07+0000",
                    updateDate="2019-08-26T09:02:49+0000",
                ),
                dict(
                    key="hotspot2",
                    message="message2",
                    component="component2",
                    vulnerabilityProbability="LOW",
                    creationDate="2011-10-26T13:34:12+0000",
                    updateDate="2020-08-31T08:19:00+0000",
                ),
            ],
        )
        self.hotspot_entities = [
            self.entity(
                key="hotspot1",
                component="component1",
                entity_type="security_hotspot",
                message="message1",
                review_priority="medium",
                creation_date="2010-12-13T10:37:07+0000",
                update_date="2019-08-26T09:02:49+0000",
            ),
            self.entity(
                key="hotspot2",
                component="component2",
                entity_type="security_hotspot",
                message="message2",
                review_priority="low",
                creation_date="2011-10-26T13:34:12+0000",
                update_date="2020-08-31T08:19:00+0000",
            ),
        ]
        self.vulnerability_entities = [
            self.entity(
                key="vulnerability1",
                component="component1",
                entity_type="vulnerability",
                message="message1",
                severity="info",
                creation_date="2020-08-30T22:48:52+0200",
                update_date="2020-09-30T22:48:52+0200",
            ),
            self.entity(
                key="vulnerability2",
                component="component2",
                entity_type="vulnerability",
                severity="major",
                creation_date="2019-08-30T22:48:52+0200",
                update_date="2019-09-30T22:48:52+0200",
                message="message2",
            ),
        ]

    async def test_all_security_warnings(self):
        """Test that all security warnings are returned."""
        self.set_source_parameter("security_types", ["vulnerability", "security_hotspot"])
        show_component_json = {}
        response = await self.collect(
            get_request_json_side_effect=[show_component_json, self.vulnerabilities_json, self.hotspots_json]
        )
        self.assert_measurement(
            response,
            value="4",
            total="100",
            entities=self.vulnerability_entities + self.hotspot_entities,
            landing_url="https://sonarqube/dashboard?id=id&branch=master",
        )

    async def test_security_warnings_hotspots_only(self):
        """Test that only the security hotspots are returned."""
        self.set_source_parameter("security_types", ["security_hotspot"])
        response = await self.collect(get_request_json_return_value=self.hotspots_json)
        self.assert_measurement(
            response,
            value="2",
            total="100",
            entities=self.hotspot_entities,
            landing_url="https://sonarqube/security_hotspots?id=id&branch=master",
        )

    async def test_security_warnings_vulnerabilities_only(self):
        """Test that by default only the vulnerabilities are returned."""
        response = await self.collect(get_request_json_return_value=self.vulnerabilities_json)
        self.assert_measurement(
            response, value="2", total="100", entities=self.vulnerability_entities, landing_url=self.issues_landing_url
        )
