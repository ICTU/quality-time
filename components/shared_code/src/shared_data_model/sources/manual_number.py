"""Manual number source."""

from shared_data_model.meta.parameter import ParameterGroup
from shared_data_model.meta.source import Source
from shared_data_model.meta.unit import Unit
from shared_data_model.parameters import IntegerParameter

MANUAL_NUMBER = Source(
    name="Manual number",
    description="A number entered manually by a Quality-time user.",
    documentation={
        "generic": """The manual number source supports all metric types that take a number as value.
Because users have to keep the value up to date by hand, this source is only meant to be used as a temporary
solution for when no automated source is available yet. For example, when the results of a security audit are only
available in a PDF-report, a 'security warnings' metric can be added with the number of findings as manual number
source.""",
    },
    parameters={
        "number": IntegerParameter(
            name="Number",
            mandatory=True,
            unit=Unit.NONE,
            metrics=[
                "commented_out_code",
                "complex_units",
                "compliance",
                "dependencies",
                "duplicated_lines",
                "failed_jobs",
                "inactive_branches",
                "issues",
                "job_runs_within_time_period",
                "loc",
                "long_units",
                "manual_test_duration",
                "manual_test_execution",
                "many_parameters",
                "merge_requests",
                "metrics",
                "missing_metrics",
                "performancetest_duration",
                "performancetest_stability",
                "pipeline_duration",
                "remediation_effort",
                "scalability",
                "security_warnings",
                "sentiment",
                "slow_transactions",
                "suppressed_violations",
                "test_suites",
                "tests",
                "todo_and_fixme_comments",
                "uncovered_branches",
                "uncovered_lines",
                "unused_jobs",
                "user_story_points",
                "velocity",
                "violations",
            ],
        ),
    },
    parameter_layout={
        "number": ParameterGroup(name="Manual source data"),
    },
)
