"""Unit tests for the OWASP Dependency Check source."""

from datetime import datetime, timedelta, timezone

from .source_collector_test_case import SourceCollectorTestCase


class OWASPDependencyCheckTest(SourceCollectorTestCase):
    """Unit tests for the OWASP Dependency Check metrics."""

    def setUp(self):
        super().setUp()
        self.sources = dict(
            sourceid=dict(type="owasp_dependency_check", parameters=dict(url="http://owasp_dependency_check.xml")))

    def test_warnings(self):
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
        response = self.collect(metric, get_request_text=xml)
        self.assert_entities(
            [dict(key="12345", url="http://owasp_dependency_check.html#l1_12345",
                  highest_severity="Medium", nr_vulnerabilities=2,
                  file_path="/home/jenkins/workspace/hackazon-owaspdep/hackazon/js/jquery.min.js")],
            response)
        self.assert_value("1", response)

    def test_low_warnings(self):
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
        response = self.collect(metric, get_request_text=xml)
        self.assert_entities(
            [dict(key="12345", url="http://owasp_dependency_check.html#l1_12345",
                  highest_severity="Low", nr_vulnerabilities=1,
                  file_path="/home/jenkins/workspace/hackazon-owaspdep/hackazon/js/jquery.min.js")],
            response)
        self.assert_value("1", response)

    def test_invalid_xml(self):
        """Test that the number of warnings is returned."""
        xml = """<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.2.1.xsd">
        </analysis>"""
        metric = dict(type="security_warnings", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_text=xml)
        self.assert_entities([], response)
        self.assert_value(None, response)
        self.maxDiff = None
        self.assert_parse_error_contains("""
AssertionError: The XML root element should be one of \
"['{https://jeremylong.github.io/DependencyCheck/dependency-check.2.0.xsd}analysis']" but is \
"{https://jeremylong.github.io/DependencyCheck/dependency-check.2.1.xsd}analysis"
""", response)

    def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        xml = """<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.2.0.xsd">
            <projectInfo>
                <reportDate>2018-10-03T13:01:24.784+0200</reportDate>
            </projectInfo>
        </analysis>"""
        metric = dict(type="source_up_to_dateness", addition="max", sources=self.sources)
        response = self.collect(metric, get_request_text=xml)
        tzinfo = timezone(timedelta(hours=2))
        expected_age = (datetime.now(tzinfo) - datetime(2018, 10, 3, 13, 1, 24, 784, tzinfo=tzinfo)).days
        self.assert_value(str(expected_age), response)
