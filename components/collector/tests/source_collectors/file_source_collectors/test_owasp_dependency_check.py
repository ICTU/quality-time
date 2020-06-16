"""Unit tests for the OWASP Dependency Check source."""

from datetime import datetime, timedelta, timezone

from source_collectors.file_source_collectors.owasp_dependency_check import OWASPDependencyCheckBase
from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class OWASPDependencyCheckTest(SourceCollectorTestCase):
    """Unit tests for the OWASP Dependency Check metrics."""

    def setUp(self):
        super().setUp()
        self.sources = dict(
            sourceid=dict(type="owasp_dependency_check", parameters=dict(url="https://owasp_dependency_check.xml")))

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
            dict(key="12345", url="https://owasp_dependency_check.html#l1_12345",
                 highest_severity="Medium", nr_vulnerabilities="2",
                 file_path="/home/jenkins/workspace/hackazon-owaspdep/hackazon/js/jquery.min.js")]
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
            dict(key="12345", url="https://owasp_dependency_check.html#l1_12345",
                 highest_severity="Low", nr_vulnerabilities="1",
                 file_path="/home/jenkins/workspace/hackazon-owaspdep/hackazon/js/jquery.min.js")]
        self.assert_measurement(response, value="1", entities=expected_entities)

    async def test_invalid_xml(self):
        """Test that the number of warnings is returned."""
        xml = """<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.1.8.xsd">
        </analysis>"""
        metric = dict(type="security_warnings", addition="sum", sources=self.sources)
        response = await self.collect(metric, get_request_text=xml)
        self.assert_measurement(
            response, value=None, entities=[], parse_error=f"""
AssertionError: The XML root element should be one of \
"{OWASPDependencyCheckBase.allowed_root_tags}" but is \
"{{https://jeremylong.github.io/DependencyCheck/dependency-check.1.8.xsd}}analysis"
""")

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
