"""Base classes for OWASP Dependency-Check JSON collector unit tests."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class OWASPDependencyCheckJSONTestCase(SourceCollectorTestCase):
    """Base class for OWASP Dependency-Check JSON collector unit tests."""

    SOURCE_TYPE = "owasp_dependency_check_json"

    def setUp(self):
        """Extend to set up test data."""
        super().setUp()
        self.file_name = "jquery.min.js"
        self.file_path = f"/home/jenkins/workspace/hackazon-owaspdep/hackazon/js/{self.file_name}"
        self.json = {
            "reportSchema": "1.1",
            "scanInfo": {"engineVersion": "6.5.3"},
            "projectInfo": {"reportDate": "2018-10-03T13:01:24.784+0200"},
            "dependencies": [
                {
                    "isVirtual": False,
                    "sha1": "12345",
                    "fileName": f"{self.file_name}",
                    "filePath": f"{self.file_path}",
                    "vulnerabilities": [
                        {"severity": "MEDIUM"},
                        {"severity": "MEDIUM"},
                    ],
                }
            ],
        }
