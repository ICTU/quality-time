"""Unit tests for the SonarQube source."""

from .base import SonarQubeTestCase


class SonarQubeSecurityWarningsTest(SonarQubeTestCase):
    """Unit tests for the SonarQube security warnings collector."""

    METRIC_TYPE = "security_warnings"
    SONARQUBE_URL = "https://sonarqube"
    API_URL = f"{SONARQUBE_URL}/api"
    LANDING_URL = f"{SONARQUBE_URL}/project"
    BRANCH = "&branch=master"
    DASHBOARD_URL = f"{SONARQUBE_URL}/dashboard?id=id{BRANCH}"
    HOTSPOTS_API = f"{API_URL}/hotspots/search?projectKey=id{BRANCH}&ps=500"
    HOTSPOTS_LANDING_URL = f"{LANDING_URL}/security_hotspots?id=id{BRANCH}"
    VULNERABILITIES_API = f"{API_URL}/issues/search?componentKeys=id&resolved=false&ps=500{BRANCH}&types=VULNERABILITY"
    VULNERABILITIES_LANDING_URL = f"{LANDING_URL}/issues?id=id{BRANCH}&resolved=false&types=VULNERABILITY"

    def setUp(self):
        """Extend to set up SonarQube security warnings."""
        super().setUp()
        self.vulnerabilities_json = {
            "total": "2",
            "issues": [
                {
                    "key": "vulnerability1",
                    "message": "message1",
                    "component": "component1",
                    "severity": "INFO",
                    "type": "VULNERABILITY",
                    "creationDate": "2020-08-30T22:48:52+0200",
                    "updateDate": "2020-09-30T22:48:52+0200",
                    "tags": ["bug"],
                },
                {
                    "key": "vulnerability2",
                    "message": "message2",
                    "component": "component2",
                    "severity": "MAJOR",
                    "type": "VULNERABILITY",
                    "creationDate": "2019-08-30T22:48:52+0200",
                    "updateDate": "2019-09-30T22:48:52+0200",
                    "tags": ["bug", "other tag"],
                },
            ],
        }
        self.hotspots_json = {
            "paging": {"total": "2"},
            "hotspots": [
                {
                    "key": "hotspot1",
                    "message": "message1",
                    "component": "component1",
                    "vulnerabilityProbability": "MEDIUM",
                    "creationDate": "2010-12-13T10:37:07+0000",
                    "updateDate": "2019-08-26T09:02:49+0000",
                    "status": "TO_REVIEW",
                },
                {
                    "key": "hotspot2",
                    "message": "message2",
                    "component": "component2",
                    "vulnerabilityProbability": "LOW",
                    "creationDate": "2011-10-26T13:34:12+0000",
                    "updateDate": "2020-08-31T08:19:00+0000",
                    "status": "REVIEWED",
                    "resolution": "FIXED",
                },
            ],
        }
        self.hotspot_entities = [
            self.entity(
                key="hotspot1",
                component="component1",
                entity_type="security_hotspot",
                message="message1",
                review_priority="medium",
                creation_date="2010-12-13T10:37:07+0000",
                update_date="2019-08-26T09:02:49+0000",
                hotspot_status="to review",
            ),
            self.entity(
                key="hotspot2",
                component="component2",
                entity_type="security_hotspot",
                message="message2",
                review_priority="low",
                creation_date="2011-10-26T13:34:12+0000",
                update_date="2020-08-31T08:19:00+0000",
                hotspot_status="fixed",
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
                tags="bug",
            ),
            self.entity(
                key="vulnerability2",
                component="component2",
                entity_type="vulnerability",
                severity="major",
                creation_date="2019-08-30T22:48:52+0200",
                update_date="2019-09-30T22:48:52+0200",
                message="message2",
                tags="bug, other tag",
            ),
        ]

    async def test_all_security_warnings(self):
        """Test that all security warnings are returned."""
        self.set_source_parameter("security_types", ["vulnerability", "security_hotspot"])
        show_component_json = {}
        response, get, post = await self.collect(
            get_request_json_side_effect=[show_component_json, self.vulnerabilities_json, self.hotspots_json],
            return_mocks=True,
        )
        get.assert_called_with(self.HOTSPOTS_API, allow_redirects=True)
        post.assert_not_called()
        self.assert_measurement(
            response,
            value="3",
            total="100",
            entities=self.vulnerability_entities + self.hotspot_entities[:1],
            landing_url=self.DASHBOARD_URL,
        )

    async def test_security_warnings_hotspots_only(self):
        """Test that only the security hotspots are returned."""
        self.set_source_parameter("security_types", ["security_hotspot"])
        response, get, post = await self.collect(get_request_json_return_value=self.hotspots_json, return_mocks=True)
        get.assert_called_with(self.HOTSPOTS_API, allow_redirects=True)
        post.assert_not_called()
        self.assert_measurement(
            response,
            value="1",
            total="100",
            entities=self.hotspot_entities[:1],
            landing_url=self.HOTSPOTS_LANDING_URL,
        )

    async def test_security_warnings_vulnerabilities_only(self):
        """Test that by default only the vulnerabilities are returned."""
        response, get, post = await self.collect(
            get_request_json_return_value=self.vulnerabilities_json, return_mocks=True
        )
        get.assert_called_with(self.VULNERABILITIES_API, allow_redirects=True)
        post.assert_not_called()
        self.assert_measurement(
            response,
            value="2",
            total="100",
            entities=self.vulnerability_entities,
            landing_url=self.VULNERABILITIES_LANDING_URL,
        )

    async def test_filter_security_warnings_hotspots_by_status(self):
        """Test that the security hotspots can be filtered by status."""
        self.set_source_parameter("security_types", ["security_hotspot"])
        self.set_source_parameter("hotspot_statuses", ["to review", "fixed"])
        response, get, post = await self.collect(get_request_json_return_value=self.hotspots_json, return_mocks=True)
        get.assert_called_with(self.HOTSPOTS_API, allow_redirects=True)
        post.assert_not_called()
        self.assert_measurement(
            response,
            value="2",
            total="100",
            entities=self.hotspot_entities,
            landing_url=self.HOTSPOTS_LANDING_URL,
        )

    async def test_filter_security_warning_vulnerabilities_by_tag(self):
        """Test that the security warning vulnerabilities can be filtered by tag."""
        self.set_source_parameter("tags", ["bug"])
        response, get, post = await self.collect(
            get_request_json_return_value=self.vulnerabilities_json, return_mocks=True
        )
        get.assert_called_with(self.VULNERABILITIES_API + "&tags=bug", allow_redirects=True)
        post.assert_not_called()
        self.assert_measurement(
            response,
            value="2",
            total="100",
            entities=self.vulnerability_entities,
            landing_url=self.VULNERABILITIES_LANDING_URL + "&tags=bug",
        )
