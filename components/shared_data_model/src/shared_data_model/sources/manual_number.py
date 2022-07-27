"""Manual number source."""

from ..meta.source import Source
from ..meta.unit import Unit
from ..parameters import IntegerParameter


MANUAL_NUMBER = Source(
    name="Manual number",
    description="A number entered manually by a Quality-time user.",
    documentation=dict(
        generic="""The manual number source supports all metric types that take a number as value.
Because users have to keep the value up to date by hand, this source is only meant to be used as a temporary
solution for when no automated source is available yet. For example, when the results of a security audit are only
available in a PDF-report, a 'security warnings' metric can be added with the number of findings as manual number
source."""
    ),
    parameters=dict(
        number=IntegerParameter(
            name="Number",
            mandatory=True,
            unit=Unit.NONE,
            metrics=[
                "accessibility",
                "commented_out_code",
                "complex_units",
                "dependencies",
                "duplicated_lines",
                "failed_jobs",
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
                "remediation_effort",
                "scalability",
                "security_warnings",
                "sentiment",
                "slow_transactions",
                "suppressed_violations",
                "test_cases",
                "tests",
                "uncovered_branches",
                "uncovered_lines",
                "unmerged_branches",
                "unused_jobs",
                "user_story_points",
                "velocity",
                "violations",
            ],
        )
    ),
)
