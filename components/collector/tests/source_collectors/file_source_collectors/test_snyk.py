"""Unit tests for the Snyk source."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase

class SnykSecurityWarningsTest(SourceCollectorTestCase):
    """Unit tests for the security warning metric."""

    def setUp(self):
        """Setup basic configs for tests"""
        super().setUp()
        self.sources = dict(source_id=dict(type="snyk", parameters=dict(url="snyk.json")))
        self.metric = dict(type="security_warnings", sources=self.sources, addition="sum")

    async def test_warnings_from_indirect_dependencies(self):
        """Test the number of security warnings indirect dependencies """
        vulnerabilities_json1 = dict(
            vulnerabilities=[
                {
                    "id": "SNYK-JS-ACORN-559469",
                    "severity": "high",
                    "from": [
                        "package.json@*",
                        "laravel-mix@4.0.16",
                        "webpack@4.41.4",
                        "acorn@6.4.0"
                    ]
                },
                {
                    "id": "SNYK-JS-AJV-584908",
                    "severity": "high",
                    "from": [
                        "package.json@*",
                        "laravel-mix@4.0.16",
                        "webpack@4.41.4",
                        "ajv@6.10.2"
                    ]
                },
                {
                    "id": "SNYK-JS-AJV-584908",
                    "severity": "high",
                    "title": "Prototype Pollution",
                    "from": [
                        "package.json@*",
                        "laravel-mix@4.0.16",
                        "extract-text-webpack-plugin@4.0.0-beta.0",
                        "schema-utils@0.4.7",
                        "ajv@6.10.2"
                    ]
                }
            ]
        )
        expected_entities = [
            dict(
                key='be02316f7d497041428a76ddb7f5ad3f',
                directdependency='laravel-mix@4.0.16',
                numbervulns=3,examplevuln='SNYK-JS-AJV-584908',
                url='https://snyk.io/vuln/SNYK-JS-AJV-584908',
                examplepath='package.json@* ➜ laravel-mix@4.0.16 ➜ webpack@4.41.4 ➜ ajv@6.10.2',
                severity='high')
                ]
        response = await self.collect(self.metric, get_request_json_return_value=vulnerabilities_json1)
        self.assert_measurement(response, value="1", entities=expected_entities)

    async def test_warnings_without_indirect_dependencies(self):
        """Test the number of security warnings from a direct dependency"""
        vulnerabilities_json = dict(
            vulnerabilities=[
                {
                    "id": "SNYK-PHP-LARAVELLARAVEL-609735",
                    "severity": "medium",
                    "title": "Improper Input Validation",
                    "from": [
                        "laravel/laravel@6.18.34"
                    ]
                },
                {
                    "id": "SNYK-PHP-LARAVELLARAVEL-609736",
                    "severity": "high",
                    "title": "Improper Input Validation",
                    "from": [
                        "laravel/laravel@6.18.34"
                    ]
                }
            ]
        )
        expected_entities = [
            dict(
                key='eca52530c6b45833ee55fb8fee9c76c4',
                directdependency='laravel/laravel@6.18.34',
                numbervulns=2,examplevuln='SNYK-PHP-LARAVELLARAVEL-609736',
                url='https://snyk.io/vuln/SNYK-PHP-LARAVELLARAVEL-609736',
                examplepath='laravel/laravel@6.18.34',
                severity='high')
                ]
        response = await self.collect(self.metric, get_request_json_return_value=vulnerabilities_json)
        self.assert_measurement(response, value="1", entities=expected_entities)
