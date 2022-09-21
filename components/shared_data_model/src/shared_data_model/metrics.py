"""Data model metrics."""

from .meta.metric import Addition, Direction, Metrics, Tag, Unit


SIG_TUVIT_EVALUATION_CRITERIA = (
    "https://www.softwareimprovementgroup.com/wp-content/uploads/SIG-TUViT-Evaluation-Criteria-Trusted-Product-"
    "Maintainability-Guidance-for-producers.pdf"
)
FOWLER_TEST_COVERAGE = "https://martinfowler.com/bliki/TestCoverage.html"
VERSION_NUMBER_EXPLANATION = """Quality-time uses the packaging library (1) to parse version numbers. The packaging
library expects version numbers to comply with PEP-440 (2). PEP is an abbrevation for Python Enhancement Proposal,
but this PEP is primarily a standard for version numbers. PEP-440 encompasses most of the semantic versioning scheme
(3) so version numbers that follow semantic versioning are usually parsed correctly."""
VERSION_NUMBER_EXPLANATION_URLS = [
    "https://pypi.org/project/packaging/",
    "https://peps.python.org/pep-0440/",
    "https://semver.org",
]

METRICS = Metrics.parse_obj(
    dict(
        accessibility=dict(
            name="Accessibility violations",
            description="The number of accessibility violations in the user interface of the software.",
            rationale="According to the W3C, 'Accessibility is essential for developers and organisations that want to "
            "create high-quality websites and web tools, and not exclude people from using their products and "
            "services' (1). Web accessibility evaluation tools can help determine if web content meets accessibility "
            "standards. Typically, these tools evaluate against one or more accessibility standards, such as the "
            "W3C Web Content Accessibility Guidelines, and report on the accessibility guidelines that are being "
            "violated.",
            rationale_urls=["https://www.w3.org/standards/webdesign/accessibility"],
            unit=Unit.VIOLATIONS,
            sources=["axecsv", "axe_core", "axe_html_reporter", "manual_number"],
            tags=[Tag.ACCESSIBILITY],
        ),
        commented_out_code=dict(
            name="Commented out code",
            description="The number of blocks of commented out lines of code.",
            rationale="Code should not be commented out because it bloats the sources and may confuse the "
            "reader as to why the code is still there, making the source code harder to understand and maintain. "
            "Unused code should be deleted. It can be retrieved from the version control system if needed.",
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
            "test because there are more execution paths that need to be tested. Complex code is harder to "
            "maintain because it is harder to understand and analyze.",
            rationale_urls=[
                SIG_TUVIT_EVALUATION_CRITERIA,
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
            description="The number of (outdated) dependencies.",
            rationale="Dependencies that are out of date can be considered a form of technical debt. On the one hand, "
            "not upgrading a dependency postpones the work of testing the new version. And, if the new version of a "
            "dependency has backwards-incompatible changes, it also postpones making adaptations to cater for those "
            "changes. On the other hand, upgrading the dependency may fix bugs and vulnerabilities, and unlock new "
            "features. Measuring the number of outdated dependencies provides insight into the size of this backlog.",
            scales=["count", "percentage"],
            unit=Unit.DEPENDENCIES,
            sources=["composer", "manual_number", "npm", "owasp_dependency_check", "pip"],
            tags=[Tag.MAINTAINABILITY],
        ),
        duplicated_lines=dict(
            name="Duplicated lines",
            description="The amount of lines that are duplicated.",
            rationale="Duplicate code makes software larger and thus potentially harder to maintain. Also, if the "
            "duplicated code contains bugs, they need to be fixed in multiple locations.",
            rationale_urls=[
                SIG_TUVIT_EVALUATION_CRITERIA,
            ],
            scales=["count", "percentage"],
            unit=Unit.LINES,
            sources=["manual_number", "sonarqube"],
            tags=[Tag.MAINTAINABILITY],
        ),
        failed_jobs=dict(
            name="Failed CI-jobs",
            description="The number of continuous integration jobs or pipelines that have failed.",
            rationale="Although it is to be expected that CI-jobs or pipelines will fail from time to time, a "
            "significant number of failed CI-jobs or pipelines over a longer period of time could be a sign that "
            "the continuous integration process is not functioning properly. Also, having many failed CI-jobs or "
            "pipelines makes it hard to see that additional jobs or pipelines start failing.",
            unit=Unit.CI_JOBS,
            near_target="5",
            sources=["azure_devops", "jenkins", "gitlab", "manual_number"],
            tags=[Tag.CI],
        ),
        issues=dict(
            name="Issues",
            description="The number of issues.",
            rationale="What exactly issues are, depends on what is available in the source. The issues metric can for "
            "example be used to count the number of open bug reports, the number of ready user stories, or the number "
            "of overdue customer service requests. For sources that support a query language, the issues to be counted "
            "can be specified using the query language of the source.",
            unit=Unit.ISSUES,
            sources=["azure_devops", "jira", "manual_number", "trello"],
        ),
        job_runs_within_time_period=dict(
            name="Job runs within time period",
            description="The number of job runs within a specified time period.",
            rationale="Deployment Frequency: Number of deployments in a given duration of time.",  # TODO - describe
            unit=Unit.CI_JOB_RUNS,
            direction=Direction.MORE_IS_BETTER,
            target="30",
            near_target="25",
            sources=["jenkins"],  # ["azure_devops", "jenkins", "gitlab", "manual_number"],
            tags=[Tag.CI],
        ),
        loc=dict(
            name="Size (LOC)",
            description="The size of the software in lines of code.",
            rationale="The size of software is correlated with the effort it takes to maintain it. Lines of code is "
            "one of the most widely used metrics to measure size of software.",
            rationale_urls=[
                SIG_TUVIT_EVALUATION_CRITERIA,
            ],
            unit=Unit.LINES,
            target="30000",
            near_target="35000",
            sources=["cloc", "manual_number", "sonarqube"],
            tags=[Tag.MAINTAINABILITY],
        ),
        long_units=dict(
            name="Long units",
            description="The amount of units (functions, methods, files) that are too long.",
            rationale="Long units are deemed harder to maintain.",
            rationale_urls=[
                SIG_TUVIT_EVALUATION_CRITERIA,
            ],
            unit=Unit.LONG_UNITS,
            scales=["count", "percentage"],
            sources=["manual_number", "sonarqube"],
            tags=[Tag.MAINTAINABILITY],
        ),
        manual_test_duration=dict(
            name="Manual test duration",
            description="The duration of the manual test in minutes.",
            rationale="Preferably, all regression tests are automated. When this is not feasible, it is good to know "
            "how much time it takes to execute the manual tests, since they need to be executed before every release.",
            unit=Unit.MINUTES,
            near_target="60",
            sources=["jira", "manual_number"],
            tags=[Tag.TEST_QUALITY],
        ),
        manual_test_execution=dict(
            name="Manual test execution",
            description="Measure the number of manual test cases that have not been tested on time.",
            rationale="Preferably, all regression tests are automated. When this is not feasible, it is good to know "
            "whether the manual regression tests have been executed recently.",
            unit=Unit.MANUAL_TEST_CASES,
            near_target="5",
            sources=["jira", "manual_number"],
            tags=[Tag.TEST_QUALITY],
        ),
        many_parameters=dict(
            name="Many parameters",
            description="The amount of units (functions, methods, procedures) that have too many parameters.",
            rationale="Units with many parameters are deemed harder to maintain.",
            rationale_urls=[
                SIG_TUVIT_EVALUATION_CRITERIA,
            ],
            scales=["count", "percentage"],
            unit=Unit.UNITS_WITH_TOO_MANY_PARAMETERS,
            sources=["manual_number", "sonarqube"],
            tags=[Tag.MAINTAINABILITY],
        ),
        merge_requests=dict(
            name="Merge requests",
            description="The amount of merge requests.",
            rationale="Merge requests need to be reviewed and approved. This metric allows for measuring the number of "
            "merge requests without the required approvals.",
            documentation="""In itself, the number of merge requests is not indicative of software quality. However, by
setting the parameter "Minimum number of upvotes", the metric can report on merge requests that have fewer than the
minimum number of upvotes. The parameter "Merge request state" can be used to exclude closed merge requests, for
example. The parameter "Target branches to include" can be used to further limit the merge requests to only count merge
requests that target specific branches, for example the "develop" branch.""",
            scales=["count", "percentage"],
            unit=Unit.MERGE_REQUESTS,
            sources=["azure_devops", "gitlab", "manual_number"],
            tags=[Tag.CI],
        ),
        metrics=dict(
            name="Metrics",
            description="The amount of metrics from one or more quality reports, with specific states and/or tags.",
            rationale="Use this metric to monitor other quality reports. For example, count the number of metrics that "
            "don't meet their target value, or count the number of metrics that have been marked as technical debt for "
            "more than two months.",
            documentation="""After adding *Quality-time* as a source to a "Metrics"-metric, one can configure which
statuses to count and which metrics to consider by filtering on report names or identifiers, on metric types, on source
types, and on tags.

```{image} screenshots/editing_quality_time_source.png
:alt: Screenshot of dialog to edit *Quality-time* source showing fields for source type, source name, and source \
    parameters such as URL, metric statuses, report names, and metric types
:class: only-light
```

```{image} screenshots/editing_quality_time_source_dark.png
:alt: Screenshot of dialog to edit *Quality-time* source showing fields for source type, source name, and source \
    parameters such as URL, metric statuses, report names, and metric types
:class: only-dark
```

```{note}
If the "Metrics" metric is itself part of the set of metrics it counts, a peculiar situation may occur: when you've
configured the "Metrics" to count red metrics and its target is not met, the metric itself will become red and thus be
counted as well. For example, if the target is at most five red metrics, and the number of red metrics increases from
five to six, the "Metrics" value will go from five to seven. You can prevent this by making sure the "Metrics" metric is
not in the set of counted metrics, for example by putting it in a different report and only count metrics in the other
report(s).
```""",
            scales=["count", "percentage"],
            unit=Unit.METRICS,
            near_target="5",
            sources=["manual_number", "quality_time"],
        ),
        missing_metrics=dict(
            name="Missing metrics",
            description="The amount of metrics that can be added to each report, but have not been added yet.",
            rationale="Provide an overview of metrics still to be added to the quality report. If metrics will not be "
            "added, a reason can be documented.",
            scales=["count", "percentage"],
            unit=Unit.MISSING_METRICS,
            near_target="5",
            sources=["manual_number", "quality_time"],
        ),
        performancetest_duration=dict(
            name="Performancetest duration",
            description="The duration of the performancetest in minutes.",
            rationale="Performance tests, especially endurance tests, may need to run for a minimum duration to give "
            "relevant results.",
            unit=Unit.MINUTES,
            addition=Addition.MIN,
            direction=Direction.MORE_IS_BETTER,
            target="30",
            near_target="25",
            sources=["gatling", "jmeter_csv", "manual_number", "performancetest_runner"],
            tags=[Tag.PERFORMANCE],
        ),
        performancetest_stability=dict(
            name="Performancetest stability",
            description="The duration of the performancetest at which throughput or error count increases.",
            rationale="When testing endurance, the throughput and error count should remain stable for the complete "
            "duration of the performancetest. If throughput or error count starts to increase during the "
            "performancetest, this may indicate memory leaks or other resource problems.",
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
            rationale="To better plan the work to remediate violations, it is helpful to have an estimate of the "
            "amount of effort it takes to remediate them.",
            rationale_urls=[
                "https://docs.sonarqube.org/latest/user-guide/metric-definitions/",
            ],
            unit=Unit.MINUTES,
            target="60",
            near_target="600",
            sources=["manual_number", "sonarqube"],
            tags=[Tag.MAINTAINABILITY],
        ),
        scalability=dict(
            name="Scalability",
            description="The number of virtual users (or percentage of the maximum number of virtual users) at "
            "which ramp-up of throughput breaks.",
            rationale="When stress testing, the load on the system-under-test has to increase sufficiently to detect "
            "the point at which the system breaks, as indicated by increasing throughput or error counts. If this "
            "breakpoint is not detected, the load has not been increased enough.",
            scales=["count", "percentage"],
            unit=Unit.VIRTUAL_USERS,
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
            rationale="Transations slower than their target response time indicate performance problems that need "
            "attention.",
            unit=Unit.TRANSACTIONS,
            near_target="5",
            sources=["gatling", "manual_number", "jmeter_csv", "jmeter_json", "performancetest_runner"],
            tags=[Tag.PERFORMANCE],
        ),
        source_up_to_dateness=dict(
            name="Source up-to-dateness",
            description="The number of days since the source was last updated.",
            rationale="If the information provided by sources is outdated, so will be the metrics in Quality-time. "
            "Hence it is important to monitor that sources are up-to-date.",
            unit=Unit.DAYS,
            addition=Addition.MAX,
            target="3",
            near_target="7",
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
        software_version=dict(
            name="Software version",
            description="The version number of the software as analyzed by the source.",
            rationale="Monitor that the version of the software is at least a specific version or get notified when "
            "the software version becomes higher than a specific version.",
            explanation=VERSION_NUMBER_EXPLANATION,
            explanation_urls=VERSION_NUMBER_EXPLANATION_URLS,
            scales=["version_number"],
            addition=Addition.MIN,
            direction=Direction.MORE_IS_BETTER,
            target="1.0",
            near_target="0.9",
            sources=[
                "performancetest_runner",
                "sonarqube",
            ],
            tags=[Tag.CI],
        ),
        source_version=dict(
            name="Source version",
            description="The version number of the source.",
            rationale="Monitor that the version of a source is at least a specific version or get notified when the "
            "version becomes higher than a specific version.",
            explanation=VERSION_NUMBER_EXPLANATION,
            explanation_urls=VERSION_NUMBER_EXPLANATION_URLS,
            scales=["version_number"],
            addition=Addition.MIN,
            direction=Direction.MORE_IS_BETTER,
            target="1.0",
            near_target="0.9",
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
            rationale="Monitor security warnings about the software, its source code, dependencies, or infrastructure "
            "so vulnerabilities can be fixed before they end up in production.",
            unit=Unit.SECURITY_WARNINGS,
            near_target="5",
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
            rationale="Satisfaction is how fulfilled developers feel with their work, team, tools, or culture; "
            "well-being is how healthy and happy they are, and how their work impacts it. Measuring satisfaction "
            "and well-being can be beneficial for understanding productivity and perhaps even for predicting it. "
            "For example, productivity and satisfaction are correlated, and it is possible that satisfaction could "
            "serve as a leading indicator for productivity; a decline in satisfaction and engagement could signal "
            "upcoming burnout and reduced productivity.",
            rationale_urls=[
                "https://queue.acm.org/detail.cfm?id=3454124",
            ],
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
            rationale="Some tools allow for suppression of violations. Having the number of suppressed violations "
            "violations visible in Quality-time allows for a double check of the suppressions.",
            scales=["count", "percentage"],
            unit=Unit.SUPPRESSED_VIOLATIONS,
            sources=["manual_number", "sonarqube"],
            tags=[Tag.MAINTAINABILITY],
        ),
        test_cases=dict(
            name="Test cases",
            description="The amount of test cases.",
            rationale="Track the test results of test cases so there is traceability from the test cases, "
            "defined in Jira, to the test results in test reports produced by tools such as Robot Framework or Junit.",
            documentation="""The test cases metric reports on the number of test cases, and their test results. The
test case metric is different than other metrics because it combines data from two types of sources: it needs one or
more sources for the test cases, and one or more sources for the test results. The test case metric then matches the
test results with the test cases.

Currently, only {index}`Jira` is supported as source for the test cases. {index}`JUnit`, {index}`TestNG`, and
{index}`Robot Framework` are supported as source for the test results. So, to configure the test cases metric, you need
to add at least one Jira source and one JUnit, TestNG, Robot Framework source. In addition, to allow the test case
metric to match test cases from Jira with test results from the JUnit, TestNG, or Robot Framework XML files, the test
results should mention Jira issue keys in their title or description.

Suppose you have configured Jira with the query: `project = "My Project" and type = "Logical Test Case"` and this
results in these test cases:

| Key  | Summary     |
|------|-------------|
| MP-1 | Test case 1 |
| MP-2 | Test case 2 |
| MP-3 | Test case 3 |
| MP-4 | Test case 4 |

Also suppose your JUnit XML has the following test results:

```xml
<testsuite tests="5" errors="0" failures="1" skipped="1">
    <testcase name="MP-1; step 1">
        <failure />
    </testcase>
    <testcase name="MP-1; step 2">
        <skipped />
    </testcase>
    <testcase name="MP-2">
        <skipped />
    </testcase>
    <testcase name="MP-3; step 1"/>
    <testcase name="MP-3; step 2"/>
</testsuite>
```

The test case metric will combine the JUnit XML file with the test cases from Jira and report one failed, one skipped,
one passed, and one untested test case:

| Key  | Summary     | Test result |
|------|-------------|-------------|
| MP-1 | Test case 1 | failed      |
| MP-2 | Test case 2 | skipped     |
| MP-3 | Test case 3 | passed      |
| MP-4 | Test case 4 | untested    |

If multiple test results in the JUnit, TestNG, or Robot Framework XML file map to one Jira test case (as with MP-1 and
MP-3 above), the 'worst' test result is reported. Possible test results from worst to best are: errored, failed,
skipped, and passed. Test cases not found in the test results are listed as untested (as with MP-4 above).""",
            scales=["count", "percentage"],
            unit=Unit.TEST_CASES,
            direction=Direction.MORE_IS_BETTER,
            near_target="0",
            sources=["jenkins_test_report", "jira", "junit", "manual_number", "robot_framework", "testng"],
            tags=[Tag.TEST_QUALITY],
        ),
        tests=dict(
            name="Tests",
            description="The amount of tests.",
            rationale="Keep track of the total number of tests or the number of tests with different states, "
            "for example failed or errored.",
            scales=["count", "percentage"],
            unit=Unit.TESTS,
            direction=Direction.MORE_IS_BETTER,
            near_target="0",
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
            rationale="Keep track of the time remaining until for example a release date, the end date of a policy, "
            "or the next team building retreat.",
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
            rationale="Code branches not covered by tests may contain bugs and signal incomplete tests.",
            rationale_urls=[FOWLER_TEST_COVERAGE],
            scales=["count", "percentage"],
            unit=Unit.UNCOVERED_BRANCHES,
            near_target="100",
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
            rationale="Code lines not covered by tests may contain bugs and signal incomplete tests.",
            rationale_urls=[FOWLER_TEST_COVERAGE],
            scales=["count", "percentage"],
            unit=Unit.UNCOVERED_LINES,
            near_target="100",
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
            rationale="It is strange if branches have had no activity for a while and have not been merged to the "
            "default branch. Maybe commits have been cherry picked, or maybe the work has been postponed, but it "
            "also sometimes happen that someone simply forgets to merge the branch.",
            documentation="""To change how soon *Quality-time* should consider branches to be inactive, use the
parameter "Number of days since last commit after which to consider branches inactive".

What exactly is the default branch is configured in GitLab or Azure DevOps. If you want to use a different branch
as default branch, you need to configure this in the source, see the documentation for
[GitLab](https://docs.gitlab.com/ee/user/project/repository/branches/default.html) or
[Azure DevOps](https://docs.microsoft.com/en-us/azure/devops/repos/git/manage-your-branches?view=azure-devops#\
change-your-default-branch).""",
            unit=Unit.BRANCHES,
            near_target="5",
            sources=["azure_devops", "gitlab", "manual_number"],
            tags=[Tag.CI],
        ),
        unused_jobs=dict(
            name="Unused CI-jobs",
            description="The number of continuous integration jobs that are unused.",
            rationale="Removing unused, obsolete CI-jobs helps to keep a clear overview of the relevant CI-jobs.",
            unit=Unit.CI_JOBS,
            near_target="5",
            sources=["azure_devops", "gitlab", "jenkins", "manual_number"],
            tags=[Tag.CI],
        ),
        user_story_points=dict(
            name="User story points",
            description="The total number of points of a selection of user stories.",
            rationale="Keep track of the number of user story points so the team has sufficient 'ready' stories to "
            "plan the next sprint.",
            unit=Unit.USER_STORY_POINTS,
            direction=Direction.MORE_IS_BETTER,
            target="100",
            near_target="75",
            sources=["azure_devops", "jira", "manual_number"],
            tags=[Tag.PROCESS_EFFICIENCY],
        ),
        velocity=dict(
            name="Velocity",
            description="The average number of user story points delivered in recent sprints.",
            rationale="Keep track of the velocity so the team knows how many story points need at least be 'ready' "
            "to plan the next sprint",
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
            rationale="The more programming rules are violated, the harder it may be to understand and maintain the "
            "software.",
            rationale_urls=[
                "https://docs.sonarqube.org/latest/user-guide/rules/",
                "https://martinfowler.com/bliki/CodeSmell.html",
            ],
            unit=Unit.VIOLATIONS,
            sources=["manual_number", "ojaudit", "sonarqube"],
            tags=[Tag.MAINTAINABILITY],
        ),
    )
)
