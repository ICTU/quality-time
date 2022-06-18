"""Data model subjects."""

from .meta.subject import Subjects


SUBJECTS = Subjects.parse_obj(
    dict(
        ci=dict(
            name="CI-environment",
            description="A continuous integration environment.",
            metrics=[
                "failed_jobs",
                "merge_requests",
                "performancetest_duration",
                "source_code_version",
                "source_up_to_dateness",
                "source_version",
                "unmerged_branches",
                "unused_jobs",
            ],
        ),
        process=dict(
            name="Process",
            description="A software development and/or maintenance process.",
            metrics=[
                "issues",
                "manual_test_duration",
                "manual_test_execution",
                "merge_requests",
                "source_up_to_dateness",
                "time_remaining",
                "unmerged_branches",
                "user_story_points",
                "velocity",
                "sentiment",
            ],
        ),
        report=dict(
            name="Quality report",
            description="A software quality report.",
            metrics=["metrics", "missing_metrics"],
        ),
        software=dict(
            name="Software",
            description="A custom software application or component.",
            metrics=[
                "accessibility",
                "commented_out_code",
                "complex_units",
                "dependencies",
                "duplicated_lines",
                "issues",
                "loc",
                "long_units",
                "manual_test_duration",
                "manual_test_execution",
                "many_parameters",
                "merge_requests",
                "performancetest_duration",
                "performancetest_stability",
                "remediation_effort",
                "scalability",
                "security_warnings",
                "slow_transactions",
                "source_code_version",
                "source_up_to_dateness",
                "source_version",
                "suppressed_violations",
                "test_cases",
                "tests",
                "uncovered_branches",
                "uncovered_lines",
                "unmerged_branches",
                "user_story_points",
                "violations",
            ],
        ),
    )
)
