"""Data model metrics."""

from .meta.metric import Addition, Direction, Metrics, Tag, Unit


METRICS = Metrics.parse_obj(
    dict(
        accessibility=dict(
            name="Accessibility violations",
            description="The number of accessibility violations in the web user interface of the software.",
            rationale="According to the W3C, 'Accessibility is essential for developers and organizations that want to "
            "create high quality websites and web tools, and not exclude people from using their products and "
            "services.' Web accessibility evaluation tools can help determine if web content meets accessibility "
            "standards. Typically, these tools evaluate against one or more accessibility standards, such as the "
            "W3C Web Content Accessibility Guidelines, and report on the accessibility guidelines that are being "
            "violated.",
            rationale_urls=["https://www.w3.org/standards/webdesign/accessibility"],
            unit=Unit.VIOLATIONS,
            default_source="axecsv",
            sources=["axecsv", "axe_core", "axe_html_reporter", "manual_number"],
            tags=[Tag.ACCESSIBILITY],
        ),
        commented_out_code=dict(
            name="Commented out code",
            description="The number of blocks of commented out lines of code.",
            rationale="Code should not be commented out because it bloats the sources and may confuse the reader as to "
            "why the code is still there. Unused code should be deleted. It can be retrieved from the version "
            "control system if needed.",
            rationale_urls=[
                "https://rules.sonarsource.com/python/RSPEC-125",
                "https://kentcdodds.com/blog/please-dont-commit-commented-out-code",
            ],
            unit=Unit.BLOCKS,
            near_target="100",
            sources=["manual_number", "sonarqube"],
            tags=[Tag.MAINTAINABILITY],
        ),
        complex_units=dict(
            name="Complex units",
            description="The amount of units (classes, functions, methods, files) that are too complex.",
            rationale="Complex code makes software harder to test and harder to maintain. Complex code is harder to "
            "test because there are more execution paths, that need to be tested. Complex code is harder to "
            "maintain because it is harder to understand and analyze.",
            rationale_urls=[
                "https://www.softwareimprovementgroup.com/wp-content/uploads/2021-SIG-TUViT-Evaluation-Criteria-"
                "Trusted-Product-Maintainability-Guidance-for-producers.pdf",
                "https://blog.codacy.com/an-in-depth-explanation-of-code-complexity/",
                "https://blog.sonarsource.com/cognitive-complexity-because-testability-understandability",
            ],
            scales=["count", "percentage"],
            unit=Unit.COMPLEX_UNITS,
            sources=["manual_number", "sonarqube"],
            tags=[Tag.MAINTAINABILITY, Tag.TESTABILITY],
        ),
        dependencies=dict(
            name="Dependencies",
            description="The amount of (outdated) dependencies.",
            rationale="Dependencies that are out of date can be considered a form of technical debt. On the one hand, "
            "not upgrading a dependency postpones the work of testing the new version. And, if the new version of "
            "dependency has backwards-incompatiable changes, it also postpones making adaptations to cater for those "
            "changes. On the other hand, upgrading the dependency may fix bugs and vulnerabilities, and unlock new "
            "features. Measuring the number of outdated dependencies provides insight into the size of this backlog.",
            scales=["count", "percentage"],
            unit=Unit.DEPENDENCIES,
            default_source="npm",
            sources=["composer", "manual_number", "npm", "owasp_dependency_check", "pip"],
            tags=[Tag.MAINTAINABILITY],
        ),
        duplicated_lines=dict(
            name="Duplicated lines",
            description="The amount of lines that are duplicated.",
            scales=["count", "percentage"],
            unit=Unit.LINES,
            sources=["manual_number", "sonarqube"],
            tags=[Tag.MAINTAINABILITY],
        ),
        failed_jobs=dict(
            name="Failed CI-jobs",
            description="The number of continuous integration jobs or pipelines that have failed.",
            unit=Unit.CI_JOBS,
            near_target="5",
            default_source="jenkins",
            sources=["azure_devops", "jenkins", "gitlab", "manual_number"],
            tags=[Tag.CI],
        ),
        issues=dict(
            name="Issues",
            description="The number of issues.",
            unit=Unit.ISSUES,
            default_source="jira",
            sources=["azure_devops", "jira", "manual_number", "trello"],
        ),
        loc=dict(
            name="Size (LOC)",
            description="The size of the software in lines of code.",
            unit=Unit.LINES,
            target="30000",
            near_target="35000",
            default_source="sonarqube",
            sources=["cloc", "manual_number", "sonarqube"],
            tags=[Tag.MAINTAINABILITY],
        ),
        long_units=dict(
            name="Long units",
            description="The amount of units (functions, methods, files) that are too long.",
            unit=Unit.LONG_UNITS,
            scales=["count", "percentage"],
            sources=["manual_number", "sonarqube"],
            tags=[Tag.MAINTAINABILITY],
        ),
        manual_test_duration=dict(
            name="Manual test duration",
            description="The duration of the manual test in minutes.",
            unit=Unit.MINUTES,
            near_target="60",
            sources=["jira", "manual_number"],
            tags=[Tag.TEST_QUALITY],
        ),
        manual_test_execution=dict(
            name="Manual test execution",
            description="Measure the number of manual test cases that have not been tested on time.",
            unit=Unit.MANUAL_TEST_CASES,
            near_target="5",
            sources=["jira", "manual_number"],
            tags=[Tag.TEST_QUALITY],
        ),
        many_parameters=dict(
            name="Many parameters",
            description="The amount of units (functions, methods, procedures) that have too many parameters.",
            scales=["count", "percentage"],
            unit=Unit.UNITS_WITH_TOO_MANY_PARAMETERS,
            sources=["manual_number", "sonarqube"],
            tags=[Tag.MAINTAINABILITY],
        ),
        merge_requests=dict(
            name="Merge requests",
            description="The amount of merge requests.",
            scales=["count", "percentage"],
            unit=Unit.MERGE_REQUESTS,
            default_source="gitlab",
            sources=["azure_devops", "gitlab", "manual_number"],
            tags=[Tag.CI],
        ),
        metrics=dict(
            name="Metrics",
            description="The amount of metrics from one or more quality reports, with specific states and/or tags.",
            scales=["count", "percentage"],
            unit=Unit.METRICS,
            near_target="5",
            sources=["manual_number", "quality_time"],
        ),
        missing_metrics=dict(
            name="Missing metrics",
            description="Count the number of metrics that can be added to each report, but have not been added yet.",
            scales=["count", "percentage"],
            unit=Unit.MISSING_METRICS,
            near_target="5",
            sources=["manual_number", "quality_time"],
        ),
        performancetest_duration=dict(
            name="Performancetest duration",
            description="The duration of the performancetest in minutes.",
            unit=Unit.MINUTES,
            addition=Addition.MIN,
            direction=Direction.MORE_IS_BETTER,
            target="30",
            near_target="25",
            default_source="jmeter_csv",
            sources=["gatling", "jmeter_csv", "manual_number", "performancetest_runner"],
            tags=[Tag.PERFORMANCE],
        ),
        performancetest_stability=dict(
            name="Performancetest stability",
            description="The duration of the performancetest at which throughput or error count increases.",
            scales=["percentage"],
            unit=Unit.MINUTES,
            addition=Addition.MIN,
            direction=Direction.MORE_IS_BETTER,
            target="100",
            near_target="90",
            sources=["manual_number", "performancetest_runner"],
            tags=[Tag.PERFORMANCE],
        ),
        remediation_effort=dict(
            name="Violation remediation effort",
            description="The amount of effort it takes to remediate violations.",
            unit=Unit.MINUTES,
            target="60",
            near_target="600",
            sources=["manual_number", "sonarqube"],
            tags=[Tag.MAINTAINABILITY],
        ),
        scalability=dict(
            name="Scalability",
            description="The percentage of (max) users at which ramp-up of throughput breaks.",
            scales=["percentage"],
            unit=Unit.USERS,
            addition=Addition.MIN,
            direction=Direction.MORE_IS_BETTER,
            target="75",
            near_target="50",
            sources=["manual_number", "performancetest_runner"],
            tags=[Tag.PERFORMANCE],
        ),
        slow_transactions=dict(
            name="Slow transactions",
            description="The number of transactions slower than their target response time.",
            unit=Unit.TRANSACTIONS,
            near_target="5",
            default_source="jmeter_csv",
            sources=["gatling", "manual_number", "jmeter_csv", "jmeter_json", "performancetest_runner"],
            tags=[Tag.PERFORMANCE],
        ),
        source_up_to_dateness=dict(
            name="Source up-to-dateness",
            description="The number of days since the source was last updated.",
            unit=Unit.DAYS,
            addition=Addition.MAX,
            target="3",
            near_target="7",
            default_source="sonarqube",
            sources=[
                "anchore",
                "anchore_jenkins_plugin",
                "axe_core",
                "azure_devops",
                "bandit",
                "calendar",
                "cobertura",
                "cobertura_jenkins_plugin",
                "cxsast",
                "gatling",
                "gitlab",
                "jacoco",
                "jacoco_jenkins_plugin",
                "jenkins",
                "jenkins_test_report",
                "jmeter_csv",
                "junit",
                "ncover",
                "robot_framework",
                "openvas",
                "owasp_dependency_check",
                "owasp_zap",
                "performancetest_runner",
                "quality_time",
                "robot_framework_jenkins_plugin",
                "sonarqube",
                "testng",
                "trello",
            ],
            tags=[Tag.CI],
        ),
        source_version=dict(
            name="Source version",
            description="The version number of the source.",
            scales=["version_number"],
            addition=Addition.MIN,
            direction=Direction.MORE_IS_BETTER,
            target="1.0",
            near_target="0.9",
            default_source="owasp_dependency_check",
            sources=[
                "axe_core",
                "cloc",
                "cobertura",
                "cxsast",
                "gatling",
                "gitlab",
                "jenkins",
                "jira",
                "openvas",
                "owasp_dependency_check",
                "owasp_zap",
                "quality_time",
                "robot_framework",
                "sonarqube",
            ],
            tags=[Tag.CI],
        ),
        security_warnings=dict(
            name="Security warnings",
            description="The number of security warnings about the software.",
            unit=Unit.SECURITY_WARNINGS,
            near_target="5",
            default_source="owasp_dependency_check",
            sources=[
                "anchore",
                "anchore_jenkins_plugin",
                "bandit",
                "cxsast",
                "manual_number",
                "openvas",
                "owasp_dependency_check",
                "owasp_zap",
                "pyupio_safety",
                "sarif_json",
                "snyk",
                "generic_json",
                "sonarqube",
            ],
            tags=[Tag.SECURITY],
        ),
        sentiment=dict(
            name="Sentiment",
            description="How are the team members feeling?",
            unit=Unit.NONE,
            addition=Addition.MIN,
            direction=Direction.MORE_IS_BETTER,
            target="10",
            near_target="8",
            sources=["manual_number"],
        ),
        suppressed_violations=dict(
            name="Suppressed violations",
            description="The amount of violations suppressed in the source.",
            scales=["count", "percentage"],
            unit=Unit.SUPPRESSED_VIOLATIONS,
            sources=["manual_number", "sonarqube"],
            tags=[Tag.MAINTAINABILITY],
        ),
        test_cases=dict(
            name="Test cases",
            description="The amount of test cases.",
            scales=["count", "percentage"],
            unit=Unit.TEST_CASES,
            direction=Direction.MORE_IS_BETTER,
            near_target="0",
            default_source="jira",
            sources=["jenkins_test_report", "jira", "junit", "manual_number", "robot_framework", "testng"],
            tags=[Tag.TEST_QUALITY],
        ),
        tests=dict(
            name="Tests",
            description="The amount of tests.",
            scales=["count", "percentage"],
            unit=Unit.TESTS,
            direction=Direction.MORE_IS_BETTER,
            near_target="0",
            default_source="jenkins_test_report",
            sources=[
                "azure_devops",
                "gatling",
                "jenkins_test_report",
                "jmeter_csv",
                "jmeter_json",
                "junit",
                "manual_number",
                "performancetest_runner",
                "robot_framework",
                "robot_framework_jenkins_plugin",
                "sonarqube",
                "testng",
            ],
            tags=[Tag.TEST_QUALITY],
        ),
        time_remaining=dict(
            name="Time remaining",
            description="The number of days remaining until a date in the future.",
            direction=Direction.MORE_IS_BETTER,
            unit=Unit.DAYS,
            addition=Addition.MIN,
            target="28",
            near_target="14",
            sources=["calendar"],
        ),
        uncovered_branches=dict(
            name="Test branch coverage",
            description="The amount of code branches not covered by tests.",
            scales=["count", "percentage"],
            unit=Unit.UNCOVERED_BRANCHES,
            near_target="100",
            default_source="sonarqube",
            sources=[
                "cobertura",
                "cobertura_jenkins_plugin",
                "jacoco",
                "jacoco_jenkins_plugin",
                "manual_number",
                "ncover",
                "sonarqube",
            ],
            tags=[Tag.TEST_QUALITY],
        ),
        uncovered_lines=dict(
            name="Test line coverage",
            description="The amount of lines of code not covered by tests.",
            scales=["count", "percentage"],
            unit=Unit.UNCOVERED_LINES,
            near_target="100",
            default_source="sonarqube",
            sources=[
                "cobertura",
                "cobertura_jenkins_plugin",
                "jacoco",
                "jacoco_jenkins_plugin",
                "manual_number",
                "ncover",
                "sonarqube",
            ],
            tags=[Tag.TEST_QUALITY],
        ),
        unmerged_branches=dict(
            name="Unmerged branches",
            description="The number of branches that have not been merged to the default branch.",
            unit=Unit.BRANCHES,
            near_target="5",
            default_source="gitlab",
            sources=["azure_devops", "gitlab", "manual_number"],
            tags=[Tag.CI],
        ),
        unused_jobs=dict(
            name="Unused CI-jobs",
            description="The number of continuous integration jobs that are unused.",
            unit=Unit.CI_JOBS,
            near_target="5",
            default_source="jenkins",
            sources=["azure_devops", "gitlab", "jenkins", "manual_number"],
            tags=[Tag.CI],
        ),
        user_story_points=dict(
            name="User story points",
            description="The total number of points of a selection of user stories.",
            unit=Unit.USER_STORY_POINTS,
            direction=Direction.MORE_IS_BETTER,
            target="100",
            near_target="75",
            default_source="azure_devops",
            sources=["azure_devops", "jira", "manual_number"],
            tags=[Tag.PROCESS_EFFICIENCY],
        ),
        velocity=dict(
            name="Velocity",
            description="The average number of user story points delivered in recent sprints.",
            unit=Unit.USER_STORY_POINTS_PER_SPRINT,
            direction=Direction.MORE_IS_BETTER,
            target="20",
            near_target="15",
            sources=["jira", "manual_number"],
            tags=[Tag.PROCESS_EFFICIENCY],
        ),
        violations=dict(
            name="Violations",
            description="The number of violations of programming rules in the software.",
            unit=Unit.VIOLATIONS,
            default_source="sonarqube",
            sources=["manual_number", "ojaudit", "sonarqube"],
            tags=[Tag.MAINTAINABILITY],
        ),
    )
)
