"""Unit tests for the SonarQube remediation effort collector."""

from .base import SonarQubeTestCase


class SonarQubeRemediationEffortTest(SonarQubeTestCase):
    """Unit tests for the SonarQube remediation effort collector."""

    METRIC_TYPE = "remediation_effort"

    def setUp(self):
        """Extend to set up some parameter values."""
        super().setUp()
        self.all_code_smells = "effort to fix all code smells"
        self.all_bug_issues = "effort to fix all bug issues"

    async def test_remediation_effort(self):
        """Test that the remediation effort is returned, as selected by the user."""
        self.set_source_parameter("effort_types", [self.all_code_smells, self.all_bug_issues])
        json = dict(
            component=dict(
                measures=[
                    dict(metric="reliability_remediation_effort", value="0"),
                    dict(metric="sqale_index", value="20"),
                ]
            )
        )
        response = await self.collect(get_request_json_return_value=json)
        self.assert_measurement(
            response,
            value="20",
            total="100",
            entities=[
                dict(
                    key="sqale_index",
                    effort_type=self.all_code_smells,
                    effort="20",
                    url=self.metric_landing_url.format("sqale_index"),
                ),
                dict(
                    key="reliability_remediation_effort",
                    effort_type=self.all_bug_issues,
                    effort="0",
                    url=self.metric_landing_url.format("reliability_remediation_effort"),
                ),
            ],
            landing_url="https://sonarqube/component_measures?id=id&branch=master",
        )

    async def test_remediation_effort_one_metric(self):
        """Test that the remediation effort is returned and that the landing url points to the metric."""
        self.set_source_parameter("effort_types", [self.all_code_smells])
        json = dict(component=dict(measures=[dict(metric="sqale_index", value="20")]))
        response = await self.collect(get_request_json_return_value=json)
        self.assert_measurement(
            response,
            value="20",
            total="100",
            entities=[
                dict(
                    key="sqale_index",
                    effort_type=self.all_code_smells,
                    effort="20",
                    url=self.metric_landing_url.format("sqale_index"),
                )
            ],
            landing_url=self.metric_landing_url.format("sqale_index"),
        )
