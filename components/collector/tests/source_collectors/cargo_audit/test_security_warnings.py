"""Unit tests for the Cargo Audit security warnings collector."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class CargoAuditSecurityWarningsTest(SourceCollectorTestCase):
    """Unit tests for the security warning metric."""

    SOURCE_TYPE = "cargo_audit"
    METRIC_TYPE = "security_warnings"

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.vulnerabilities_json = {
            "vulnerabilities": {
                "list": [
                    {
                        "advisory": {
                            "id": "RUSTSEC-2022-0090",
                            "title": "`libsqlite3-sys` via C SQLite CVE-2022-35737",
                            "url": "https://nvd.nist.gov/vuln/detail/CVE-2022-35737",
                            "aliases": [
                                "CVE-2020-26235",
                                "GHSA-wcg3-cvx6-7396",
                            ],
                        },
                        "versions": {
                            "patched": [
                                ">=0.25.1",
                            ],
                        },
                        "package": {
                            "name": "libsqlite3-sys",
                            "version": "0.24.2",
                        },
                    },
                ],
            },
            "warnings": {
                "unsound": [
                    {
                        "kind": "unsound",
                        "package": {
                            "name": "ouroboros",
                            "version": "0.15.6",
                        },
                        "advisory": {
                            "id": "RUSTSEC-2023-0042",
                            "title": "Ouroboros is Unsound",
                            "url": "https://github.com/joshua-maros/ouroboros/issues/88",
                        },
                        "versions": {"patched": [], "unaffected": []},
                    }
                ],
                "yanked": [
                    {
                        "kind": "yanked",
                        "package": {
                            "name": "h2",
                            "version": "0.3.17",
                        },
                        "advisory": None,
                        "versions": None,
                    }
                ],
            },
        }
        self.expected_entities = [
            {
                "key": "libsqlite3-sys:0_24_2:RUSTSEC-2022-0090",
                "package_name": "libsqlite3-sys",
                "package_version": "0.24.2",
                "advisory_id": "RUSTSEC-2022-0090",
                "advisory_title": "`libsqlite3-sys` via C SQLite CVE-2022-35737",
                "advisory_url": "https://nvd.nist.gov/vuln/detail/CVE-2022-35737",
                "uuid": "CVE-2020-26235",
                "versions_patched": ">=0.25.1",
                "warning_type": "vulnerability",
            },
            {
                "key": "ouroboros:0_15_6:RUSTSEC-2023-0042",
                "package_name": "ouroboros",
                "package_version": "0.15.6",
                "advisory_id": "RUSTSEC-2023-0042",
                "advisory_title": "Ouroboros is Unsound",
                "advisory_url": "https://github.com/joshua-maros/ouroboros/issues/88",
                "versions_patched": "",
                "warning_type": "unsound",
            },
            {
                "key": "h2:0_3_17:",
                "package_name": "h2",
                "package_version": "0.3.17",
                "advisory_id": "",
                "advisory_title": "",
                "advisory_url": "",
                "versions_patched": "",
                "warning_type": "yanked",
            },
        ]

    async def test_warnings(self):
        """Test the number of security warnings."""
        response = await self.collect(get_request_json_return_value=self.vulnerabilities_json)
        self.assert_measurement(response, value="3", entities=self.expected_entities)

    async def test_warnings_with_specific_types(self):
        """Test that the security warnings can be filtered by type."""
        self.set_source_parameter("warning_types", ["vulnerability", "unsound"])
        response = await self.collect(get_request_json_return_value=self.vulnerabilities_json)
        self.assert_measurement(response, value="2", entities=self.expected_entities[:2])

    async def test_warnings_with_fix(self):
        """Test that the security warnings can be filtered by fix availability."""
        self.set_source_parameter("fix_availability", ["fix available"])
        response = await self.collect(get_request_json_return_value=self.vulnerabilities_json)
        self.assert_measurement(response, value="1", entities=self.expected_entities[:1])

    async def test_warnings_without_fix(self):
        """Test that the security warnings can be filtered by fix availability."""
        self.set_source_parameter("fix_availability", ["no fix available"])
        response = await self.collect(get_request_json_return_value=self.vulnerabilities_json)
        self.assert_measurement(response, value="2", entities=self.expected_entities[1:])
