"""Unit tests for the SonarQube violations collector."""

from .base import SonarQubeTestCase


class SonarQubeViolationsTest(SonarQubeTestCase):
    """Unit tests for the SonarQube violations collector."""

    METRIC_TYPE = "violations"

    def setUp(self) -> None:
        """Extend to set up the SonarQube violations."""
        super().setUp()
        self.json = {
            "total": "2",
            "issues": [
                {
                    "key": "violation1",
                    "message": "message1",
                    "component": "component1",
                    "impacts": [{"severity": "LOW", "softwareQuality": "RELIABILITY"}],
                    "cleanCodeAttributeCategory": "CONSISTENT",
                    "creationDate": "2020-08-30T22:48:53+0200",
                    "updateDate": "2020-09-30T22:48:54+0200",
                    "tags": ["bug"],
                },
                {
                    "key": "violation2",
                    "message": "message2",
                    "component": "component2",
                    "impacts": [
                        {"severity": "MEDIUM", "softwareQuality": "MAINTAINABILITY"},
                        {"severity": "LOW", "softwareQuality": "RELIABILITY"},
                    ],
                    "cleanCodeAttributeCategory": "INTENTIONAL",
                    "creationDate": "2019-08-30T21:48:52+0200",
                    "updateDate": "2019-09-30T21:48:52+0200",
                    "tags": ["bug", "other tag"],
                },
            ],
        }
        self.expected_entities = [
            self.entity(
                key="violation1",
                component="component1",
                message="message1",
                impacts="low impact on reliability",
                clean_code_attribute_category="consistent",
                creation_date="2020-08-30T22:48:53+0200",
                update_date="2020-09-30T22:48:54+0200",
                tags="bug",
            ),
            self.entity(
                key="violation2",
                component="component2",
                message="message2",
                impacts="medium impact on maintainability, low impact on reliability",
                clean_code_attribute_category="intentional",
                creation_date="2019-08-30T21:48:52+0200",
                update_date="2019-09-30T21:48:52+0200",
                tags="bug, other tag",
            ),
        ]

    async def test_violations(self):
        """Test that the number of violations is returned."""
        response = await self.collect(get_request_json_return_value=self.json)
        self.assert_measurement(
            response,
            value="2",
            entities=self.expected_entities,
            landing_url=self.issues_landing_url,
        )

    async def test_medium_violations(self):
        """Test that the number of medium violations is returned."""
        self.set_source_parameter("impact_severities", ["medium"])
        self.json["total"] = 1
        del self.json["issues"][0]
        response = await self.collect(get_request_json_return_value=self.json)
        del self.expected_entities[0]
        self.assert_measurement(
            response,
            value="1",
            entities=self.expected_entities,
            landing_url=self.issues_landing_url + "&impactSeverities=MEDIUM",
        )

    async def test_multiple_violation_severities(self):
        """Test that the number of violations is returned and that the landing URL points to the selected severities."""
        self.set_source_parameter("impact_severities", ["low", "medium"])
        response = await self.collect(get_request_json_return_value=self.json)
        self.assert_measurement(
            response,
            value="2",
            entities=self.expected_entities,
            landing_url=self.issues_landing_url + "&impactSeverities=LOW,MEDIUM",
        )

    async def test_impacted_software_qualities(self):
        """Test that the number of violations is returned and that the landing URL points to the selected qualities."""
        self.set_source_parameter("impacted_software_qualities", ["maintainability", "reliability"])
        response = await self.collect(get_request_json_return_value=self.json)
        self.assert_measurement(
            response,
            value="2",
            entities=self.expected_entities,
            landing_url=self.issues_landing_url + "&impactSoftwareQualities=MAINTAINABILITY,RELIABILITY",
        )

    async def test_clean_code_attribute_categories(self):
        """Test that the number of violations is returned and that the landing URL points to the selected categories."""
        self.set_source_parameter("clean_code_attribute_categories", ["intentional", "consistent"])
        response = await self.collect(get_request_json_return_value=self.json)
        self.assert_measurement(
            response,
            value="2",
            entities=self.expected_entities,
            landing_url=self.issues_landing_url + "&cleanCodeAttributeCategories=CONSISTENT,INTENTIONAL",
        )

    async def test_tags(self):
        """Test that violations can be limited based on tags."""
        self.set_source_parameter("tags", ["accessibility"])
        response = await self.collect(get_request_json_return_value=self.json)
        self.assert_measurement(
            response,
            value="2",
            entities=self.expected_entities,
            landing_url=self.issues_landing_url + "&tags=accessibility",
        )
