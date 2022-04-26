"""Unit tests for the SARIF JSON security warnings collector."""

from ..source_collector_test_case import SourceCollectorTestCase


class SARIFJSONSecurityWarningsTest(SourceCollectorTestCase):
    """Unit tests for the security warning metric."""

    SOURCE_TYPE = "sarif_json"
    METRIC_TYPE = "security_warnings"

    async def test_warnings(self):
        """Test the number of security warnings."""
        vulnerabilities_json = dict(
            runs=[
                dict(
                    tool=dict(
                        driver=dict(
                            rules=[
                                dict(
                                    id="CVE-2019-18276",
                                    shortDescription=dict(text="CVE-2019-18276"),
                                    fullDescription=dict(text="An issue was discovered ..."),
                                    helpUri="https://avd.aquasec.com/nvd/cve-2019-18276",
                                )
                            ]
                        )
                    ),
                    results=[
                        dict(
                            ruleId="CVE-2019-18276",
                            ruleIndex=0,
                            level="note",
                            message=dict(
                                text="Package: bash\nInstalled Version: 5.0-6ubuntu1.1\nVulnerability ...",
                            ),
                            locations=[
                                dict(
                                    physicalLocation=dict(
                                        artifactLocation=dict(
                                            uri="docker.io/ictu/quality-time_database", uriBaseId="ROOTPATH"
                                        ),
                                        region=dict(startLine=1),
                                    )
                                )
                            ],
                        )
                    ],
                )
            ]
        )
        run = vulnerabilities_json["runs"][0]
        rule = run["tool"]["driver"]["rules"][0]
        result = run["results"][0]
        expected_entities = [
            dict(
                key="CVE-2019-18276@docker_io-ictu-quality-time_database",
                message=result["message"]["text"],
                level=result["level"],
                locations=result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"],
                rule=rule["shortDescription"]["text"],
                description=rule["fullDescription"]["text"],
                url=rule["helpUri"],
            )
        ]
        response = await self.collect(get_request_json_return_value=vulnerabilities_json)
        self.assert_measurement(response, value="1", entities=expected_entities)
