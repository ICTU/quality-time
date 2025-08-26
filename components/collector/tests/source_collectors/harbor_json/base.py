"""Base classes for Harbor JSON collector unit tests."""

from typing import ClassVar

from source_collectors.harbor_json.json_types import HarborJSON

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class HarborJSONCollectorTestCase(SourceCollectorTestCase):
    """Base class for Harbor JSON collector unit tests."""

    SOURCE_TYPE = "harbor_json"
    VULNERABILITIES_JSON: ClassVar[HarborJSON] = {
        "application/vnd.security.vulnerability.report; version=1.1": {
            "generated_at": "2023-08-26T16:32:21.923910328Z",
            "vulnerabilities": [
                {
                    "id": "CVE-2011-3374",
                    "package": "apt",
                    "version": "2.2.4",
                    "fix_version": "2.2.5",
                    "severity": "Low",
                    "description": "It was found that apt-key in apt, all versions, do not correctly validate ...",
                    "links": ["https://avd.aquasec.com/nvd/cve-2011-3374"],
                },
                {
                    "id": "CVE-2020-22218",
                    "package": "libssh2-1",
                    "version": "1.9.0-2",
                    "fix_version": "",
                    "severity": "High",
                    "description": "An issue was discovered in function _libssh2_packet_add in libssh2 1.10.0 ...",
                    "links": ["https://avd.aquasec.com/nvd/cve-2020-22218"],
                },
            ],
        },
    }
