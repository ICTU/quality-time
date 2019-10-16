"""Unit tests for the OWASP Dependency Check Jenkins plugin source."""

from datetime import datetime, timezone

from .source_collector_test_case import SourceCollectorTestCase


class OWASPDependencyCheckJenkinsPluginTest(SourceCollectorTestCase):
    """Unit tests for the OWASP Dependency Check Jenkins plugin metrics."""

    def setUp(self):
        self.sources = dict(
            sourceid=dict(
                type="owasp_dependency_check_jenkins_plugin",
                parameters=dict(url="https://jenkins/job", severities=["critical", "high", "normal"])))

    def test_warnings(self):
        """Test that the number of security warnings is returned."""
        metric = dict(type="security_warnings", addition="sum", sources=self.sources)
        response = self.collect(
            metric,
            get_request_json_return_value=dict(
                warnings=[
                    dict(fileName="/f1", priority="NORMAL"),
                    dict(fileName="/f1", priority="HIGH"),
                    dict(fileName="/f2", priority="NORMAL"),
                    dict(fileName="/f3", priority="LOW"),
                    dict(fileName="/f4", priority="CRITICAL")]))
        expected_entities = [
            dict(key="/f1", file_path="/f1", highest_severity="High", nr_vulnerabilities=2),
            dict(key="/f2", file_path="/f2", highest_severity="Normal", nr_vulnerabilities=1),
            dict(key="/f4", file_path="/f4", highest_severity="Critical", nr_vulnerabilities=1)]
        self.assert_measurement(response, value="3", entities=expected_entities)

    def test_up_to_dateness(self):
        """Test that the source age in days is returned."""
        metric = dict(type="source_up_to_dateness", addition="max", sources=self.sources)
        response = self.collect(
            metric, get_request_json_return_value=dict(timestamp="1565284457173"))
        expected_age = (datetime.now(timezone.utc) - datetime(2019, 8, 8, 17, 14, 17, 173, tzinfo=timezone.utc)).days
        self.assert_measurement(response, value=str(expected_age))
