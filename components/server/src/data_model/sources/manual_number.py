"""Manual number source."""

from ..meta.source import Source
from ..meta.unit import Unit
from ..parameters import IntegerParameter


MANUAL_NUMBER = Source(
    name="Manual number",
    description="A manual number.",
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
                "remediation_effort",
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
                "user_story_points",
                "scalability",
                "slow_transactions",
                "security_warnings",
                "suppressed_violations",
                "test_cases",
                "tests",
                "uncovered_branches",
                "uncovered_lines",
                "unmerged_branches",
                "unused_jobs",
                "velocity",
                "violations",
            ],
        )
    ),
)
