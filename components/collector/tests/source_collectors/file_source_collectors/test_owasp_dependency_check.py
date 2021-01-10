"""Unit tests for the OWASP Dependency Check source."""

from datetime import datetime, timedelta, timezone

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase

from source_collectors.file_source_collectors.owasp_dependency_check import OWASPDependencyCheckBase


class OWASPDependencyCheckTest(SourceCollectorTestCase):
    """Unit tests for the OWASP Dependency Check metrics."""

    def setUp(self):
        super().setUp()
        self.sources = dict(
            sourceid=dict(type="owasp_dependency_check", parameters=dict(url="https://owasp_dependency_check.xml"))
        )

    async def test_warnings(self):
        """Test that the number of warnings is returned."""
        xml = """<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.2.0.xsd">
            <dependency isVirtual="false">
                <sha1>12345</sha1>
                <fileName>jquery.min.js</fileName>
                <filePath>/home/jenkins/workspace/hackazon-owaspdep/hackazon/js/jquery.min.js</filePath>
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
        metric = dict(type="security_warnings", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_text=xml)
        expected_entities = [
            dict(
                key="12345",
                url="https://owasp_dependency_check.html#l1_12345",
                highest_severity="Medium",
                nr_vulnerabilities="2",
                file_name="jquery.min.js",
                file_path="/home/jenkins/workspace/hackazon-owaspdep/hackazon/js/jquery.min.js",
            )
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)

    async def test_low_warnings(self):
        """Test that the number of warnings is returned."""
        xml = """<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.2.0.xsd">
            <dependency isVirtual="false">
                <sha1>12345</sha1>
                <fileName>jquery.min.js</fileName>
                <filePath>/home/jenkins/workspace/hackazon-owaspdep/hackazon/js/jquery.min.js</filePath>
                <vulnerabilities>
                    <vulnerability source="NVD">
                        <cvssV2>
                            <severity>LOW</severity>
                        </cvssV2>
                    </vulnerability>
                </vulnerabilities>
            </dependency>
        </analysis>"""
        metric = dict(type="security_warnings", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_text=xml)
        expected_entities = [
            dict(
                key="12345",
                url="https://owasp_dependency_check.html#l1_12345",
                highest_severity="Low",
                nr_vulnerabilities="1",
                file_name="jquery.min.js",
                file_path="/home/jenkins/workspace/hackazon-owaspdep/hackazon/js/jquery.min.js",
            )
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)

    async def test_multiple_warnings_with_same_filepath(self):
        """Test that the hashes are based on both the file path and the file name."""
        xml = """<?xml version="1.0"?>
            <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.2.5.xsd">
                <dependency>
                    <fileName>CuttingEdge.Conditions:1.2.0.0</fileName>
                    <filePath>packages.config</filePath>
                    <vulnerabilities>
                        <vulnerability source="NVD">
                            <cvssV2>
                                <severity>LOW</severity>
                            </cvssV2>
                        </vulnerability>
                    </vulnerabilities>
                </dependency>
                <dependency>
                    <fileName>IdentityModel:1.13.1</fileName>
                    <filePath>packages.config</filePath>
                    <vulnerabilities>
                        <vulnerability source="NVD">
                            <cvssV2>
                                <severity>LOW</severity>
                            </cvssV2>
                        </vulnerability>
                    </vulnerabilities>
                </dependency>
            </analysis>"""
        metric = dict(type="security_warnings", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_text=xml)
        expected_entities = [
            dict(
                key="498ac4bf0c766490ad58cd04a71e07a439b97fc8",
                url="",
                file_name="CuttingEdge.Conditions:1.2.0.0",
                highest_severity="Low",
                nr_vulnerabilities="1",
                file_path="packages.config",
            ),
            dict(
                key="7f5f471406d316dfeb580de2738db563f3c7ac97",
                url="",
                file_name="IdentityModel:1.13.1",
                highest_severity="Low",
                nr_vulnerabilities="1",
                file_path="packages.config",
            ),
        ]
        self.assert_measurement(response, value="2", entities=expected_entities)

    async def test_invalid_xml(self):
        """Test that the number of warnings is returned."""
        xml = """<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.1.8.xsd">
        </analysis>"""
        metric = dict(type="security_warnings", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_text=xml)
        self.assert_measurement(
            response,
            value=None,
            entities=[],
            parse_error=f"""
AssertionError: The XML root element should be one of \
"{OWASPDependencyCheckBase.allowed_root_tags}" but is \
"{{https://jeremylong.github.io/DependencyCheck/dependency-check.1.8.xsd}}analysis"
""",
        )

    async def test_dependencies(self):
        """Test that the dependencies are returned."""
        xml = """<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.2.0.xsd">
            <dependency isVirtual="false">
                <sha1>9999</sha1>
                <fileName>jquery.min.js</fileName>
                <filePath>/home/jenkins/workspace/hackazon/js/jquery.min.js</filePath>
                <vulnerabilities>
                    <vulnerability source="NVD">
                        <cvssV2>
                            <severity>LOW</severity>
                        </cvssV2>
                    </vulnerability>
                </vulnerabilities>
            </dependency>
        </analysis>"""
        metric = dict(type="dependencies", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_text=xml)
        expected_entities = [
            dict(
                key="9999",
                url="https://owasp_dependency_check.html#l1_9999",
                file_name="jquery.min.js",
                file_path="/home/jenkins/workspace/hackazon/js/jquery.min.js",
            )
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        xml = """<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.2.0.xsd">
            <projectInfo>
                <reportDate>2018-10-03T13:01:24.784+0200</reportDate>
            </projectInfo>
        </analysis>"""
        metric = dict(type="source_up_to_dateness", addition="max", sources=self.sources)
        response = await self.collect(metric, get_request_text=xml)
        timezone_info = timezone(timedelta(hours=2))
        expected_age = (datetime.now(timezone_info) - datetime(2018, 10, 3, 13, 1, 24, 784, tzinfo=timezone_info)).days
        self.assert_measurement(response, value=str(expected_age))

    async def test_source_up_to_dateness_no_encoding(self):
        """Test that the source age in days is returned, also when the XML has no encoding specified."""
        xml = """<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.2.0.xsd">
            <projectInfo>
                <reportDate>2018-10-03T13:01:24.784+0200</reportDate>
            </projectInfo>
        </analysis>"""
        metric = dict(type="source_up_to_dateness", addition="max", sources=self.sources)
        response = await self.collect(metric, get_request_text=xml)
        timezone_info = timezone(timedelta(hours=2))
        expected_age = (datetime.now(timezone_info) - datetime(2018, 10, 3, 13, 1, 24, 784, tzinfo=timezone_info)).days
        self.assert_measurement(response, value=str(expected_age))
