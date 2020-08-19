"""Unit tests for the Snyk source."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class SnykSecurityWarningsTest(SourceCollectorTestCase):
    """Unit tests for the security warning metric."""

    async def test_warnings(self):
        """Test the number of security warnings."""
        css = "Cross Site Scripting"
        package_name = "vulnerablepackage"
        package_spec = "vulnerable_package@1.2.0"
        sources = dict(source_id=dict(type="snyk", parameters=dict(url="snyk-vuln.json", severities=["high"])))
        metric = dict(type="security_warnings", sources=sources, addition="sum")
        vulnerabilities_json = dict(
            vulnerabilities=[
                {
                    'title': css, 'id': 'SNYK-JS-LODASH-590103', 'severity': 'high',
                    'fixedIn': '3.0', 'packageName': package_name, 'version': '1.2',
                    'from': ["mainpackage@0.0.0", package_spec]},
                {
                    'title': css, 'id': 'SNYK-JS-LODASH-590103', 'severity': 'high',
                    'fixedIn': ['3.0', '3.1'], 'packageName': package_name, 'version': '1.2',
                    'from': ["mainpackage@0.0.0", "intermediatepackage@1.0", package_spec]},
                {
                    'title': 'SQL Injection', 'id': 'SNYK-JS-LODASH-590104', 'severity': 'low',
                    'fixedIn': ['3.0', '3.1'], 'packageName': package_name, 'version': '1.4.0',
                    'from': ["mainpackage@1.0.0", "vulnerablepackage@1.4.0"]}])
        expected_entities = [
            dict(
                key='c6948b61d82118ab3438d4c847879a00', cve=css, url='https://snyk.io/vuln/SNYK-JS-LODASH-590103',
                severity='high', fix='3.0', package=package_name, version='1.2', package_include=package_spec),
            dict(
                key='32317b40f5948e02fa530c5ab6380d3d', cve=css, url='https://snyk.io/vuln/SNYK-JS-LODASH-590103',
                severity='high', fix='3.0, 3.1', package=package_name, version='1.2',
                package_include=f"intermediatepackage@1.0 ➜ {package_spec}")]
        response = await self.collect(metric, get_request_json_return_value=vulnerabilities_json)
        self.assert_measurement(response, value="2", entities=expected_entities)
