"""Unit tests for the Cargo Audit security warnings collector."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class CargoAuditSecurityWarningsTest(SourceCollectorTestCase):
    """Unit tests for the security warning metric."""

    SOURCE_TYPE = "cargo_audit"
    METRIC_TYPE = "security_warnings"

    async def test_warnings(self):
        """Test the number of security warnings."""
        vulnerabilities_json = {
            "vulnerabilities": {
                "list": [
                    {
                        "advisory": {
                            "id": "RUSTSEC-2022-0090",
                            "title": "`libsqlite3-sys` via C SQLite CVE-2022-35737",
                            "url": "https://nvd.nist.gov/vuln/detail/CVE-2022-35737",
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
        }
        expected_entities = [
            {
                "key": "libsqlite3-sys:0_24_2:RUSTSEC-2022-0090",
                "package_name": "libsqlite3-sys",
                "package_version": "0.24.2",
                "advisory_id": "RUSTSEC-2022-0090",
                "advisory_title": "`libsqlite3-sys` via C SQLite CVE-2022-35737",
                "advisory_url": "https://nvd.nist.gov/vuln/detail/CVE-2022-35737",
                "versions_patched": ">=0.25.1",
            },
        ]
        response = await self.collect(get_request_json_return_value=vulnerabilities_json)
        self.assert_measurement(response, value="1", entities=expected_entities)
