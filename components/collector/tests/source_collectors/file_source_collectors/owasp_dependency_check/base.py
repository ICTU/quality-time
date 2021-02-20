"""Base classes for OWASP dependency check collector unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class OWASPDependencyCheckTestCase(SourceCollectorTestCase):
    """Base class for OWASP dependency check collector unit tests."""

    SOURCE_TYPE = "owasp_dependency_check"

    def setUp(self):
        """Extend to set up test data."""
        super().setUp()
        self.file_name = "jquery.min.js"
        self.file_path = f"/home/jenkins/workspace/hackazon-owaspdep/hackazon/js/{self.file_name}"
        self.xml = f"""<?xml version="1.0"?>
            <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.2.0.xsd">
                <projectInfo>
                    <reportDate>2018-10-03T13:01:24.784+0200</reportDate>
                </projectInfo>
                <dependency isVirtual="false">
                    <sha1>12345</sha1>
                    <fileName>{self.file_name}</fileName>
                    <filePath>{self.file_path}</filePath>
                    <vulnerabilities>
                        <vulnerability source="NVD">
                            <cvssV2>
                                <severity>MEDIUM</severity>
                            </cvssV2>
                        </vulnerability>
                        <vulnerability source="NVD">
                            <cvssV2>
                                <severity>LOW</severity>
                            </cvssV2>
                        </vulnerability>
                    </vulnerabilities>
                </dependency>
            </analysis>"""
