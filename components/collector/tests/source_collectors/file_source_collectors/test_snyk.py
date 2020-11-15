"""Unit tests for the Snyk source."""

from collector_utilities.functions import safe_entity_key

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class SnykSecurityWarningsTest(SourceCollectorTestCase):
    """Unit tests for the security warning metric."""

    def setUp(self):
        """Setup basic configs for tests"""
        super().setUp()
        self.sources = dict(source_id=dict(type="snyk", parameters=dict(url="snyk.json")))
        self.metric = dict(type="security_warnings", sources=self.sources, addition="sum")
        self.direct_dependency = "laravel-mix@4.0.16"
        self.direct_dependency_key = safe_entity_key(self.direct_dependency)
        self.direct_dependency_path = ["package.json@*", self.direct_dependency]
        self.vulnerabilities_json = dict(
            vulnerabilities=[
                {
                    "id": "SNYK-JS-ACORN-559469",
                    "severity": "low",
                    "from": self.direct_dependency_path + ["webpack@4.41.4", "acorn@6.4.0"]
                }
            ]
        )
        self.expected_entity = dict(
            key=self.direct_dependency_key,
            dependency=self.direct_dependency,
            nr_vulnerabilities=1, example_vulnerability='SNYK-JS-ACORN-559469',
            url='https://snyk.io/vuln/SNYK-JS-ACORN-559469',
            example_path='package.json@* ➜ laravel-mix@4.0.16 ➜ webpack@4.41.4 ➜ acorn@6.4.0',
            highest_severity='low')

    async def test_one_low_severity_warning(self):
        """Test only low severity warnings."""
        response = await self.collect(self.metric, get_request_json_return_value=self.vulnerabilities_json)
        self.assert_measurement(response, value="1", entities=[self.expected_entity])

    async def test_minimum_severity(self):
        """Test that security warnings with a lower severity than selected are ignored."""
        self.sources["source_id"]["parameters"]["severities"] = ["medium", "high"]
        response = await self.collect(self.metric, get_request_json_return_value=self.vulnerabilities_json)
        self.assert_measurement(response, value="0", entities=[])

    async def test_one_warning_with_multiple_severities(self):
        """Test that multiple warnings are combined for one top-level dependency."""
        self.vulnerabilities_json["vulnerabilities"].extend([
            {
                "id": "SNYK-JS-AJV-584908",
                "severity": "medium",
                "from": self.direct_dependency_path + ["webpack@4.41.4", "ajv@6.10.2"]
            },
            {
                "id": "SNYK-JS-AJV-584908",
                "severity": "low",
                "title": "Prototype Pollution",
                "from": self.direct_dependency_path + [
                    "extract-text-webpack-plugin@4.0.0-beta.0", "schema-utils@0.4.7", "ajv@6.10.2"]
            }
        ])
        expected_entities = [
            dict(
                key=self.direct_dependency_key,
                dependency=self.direct_dependency,
                nr_vulnerabilities=3, example_vulnerability='SNYK-JS-AJV-584908',
                url='https://snyk.io/vuln/SNYK-JS-AJV-584908',
                example_path='package.json@* ➜ laravel-mix@4.0.16 ➜ extract-text-webpack-plugin@4.0.0-beta.0 ➜ '
                             'schema-utils@0.4.7 ➜ ajv@6.10.2',
                highest_severity='medium'
            )
        ]
        response = await self.collect(self.metric, get_request_json_return_value=self.vulnerabilities_json)
        self.assert_measurement(response, value="1", entities=expected_entities)

    async def test_warning_without_indirect_dependencies(self):
        """Test that warnings are also collected if they have no indirect dependencies."""
        self.vulnerabilities_json["vulnerabilities"].append(
            {
                "id": "SNYK-PHP-LARAVELLARAVEL-609736", "severity": "high", "title": "Improper Input Validation",
                "from": ["laravel/laravel@6.18.34"]
            }
        )
        expected_entities = [
            self.expected_entity,
            dict(
                key='laravel-laravel@6_18_34',
                dependency='laravel/laravel@6.18.34',
                nr_vulnerabilities=1, example_vulnerability='SNYK-PHP-LARAVELLARAVEL-609736',
                url='https://snyk.io/vuln/SNYK-PHP-LARAVELLARAVEL-609736',
                example_path='laravel/laravel@6.18.34',
                highest_severity='high')]
        response = await self.collect(self.metric, get_request_json_return_value=self.vulnerabilities_json)
        self.assert_measurement(response, value="2", entities=expected_entities)
