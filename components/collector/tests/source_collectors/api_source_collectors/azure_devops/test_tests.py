"""Unit tests for the Azure Devops Server tests collector."""

from .base import AzureDevopsTestCase


class AzureDevopsTestsTest(AzureDevopsTestCase):
    """Unit tests for the Azure DevOps Server tests collector."""

    async def test_nr_of_tests(self):
        """Test that the number of tests is returned."""
        self.sources["source_id"]["parameters"]["test_result"] = ["passed"]
        self.sources["source_id"]["parameters"]["test_run_names_to_include"] = ["A.*"]
        self.sources["source_id"]["parameters"]["test_run_states_to_include"] = ["completed"]
        metric = dict(type="tests", sources=self.sources, addition="sum")
        response = await self.collect(
            metric,
            get_request_json_return_value=dict(
                value=[
                    dict(id=1, name="A", build=dict(id="1"), state="Completed", passedTests=2, totalTests=2),
                    dict(
                        id=2,
                        name="A",
                        build=dict(id="2"),
                        state="Completed",
                        startedDate="2020-06-20T14:56:00.58Z",
                        completedDate="2020-06-20T14:56:00.633Z",
                        passedTests=2,
                        notApplicableTests=1,
                        totalTests=3,
                        webAccessUrl="https://azuredevops/project/run",
                    ),
                    dict(id=3, name="A", build=dict(id="1"), state="Completed", passedTests=4, totalTests=4),
                    dict(id=4, name="A", build=dict(id="2"), state="Completed", passedTests=1, totalTests=1),
                    dict(id=5, name="B", build=dict(id="3"), state="Completed", passedTests=5, totalTests=5),
                    dict(id=6, name="A+", build=dict(id="1"), state="Completed", passedTests=6, totalTests=6),
                    dict(id=7, name="A+", build=dict(id="2"), state="InProgress", passedTests=6, totalTests=6),
                ]
            ),
        )
        self.assert_measurement(
            response,
            value="9",
            total="10",
            entities=[
                dict(
                    key="2",
                    name="A",
                    state="Completed",
                    build_id="2",
                    started_date="2020-06-20T14:56:00.58Z",
                    completed_date="2020-06-20T14:56:00.633Z",
                    counted_tests="2",
                    incomplete_tests="0",
                    not_applicable_tests="1",
                    passed_tests="2",
                    unanalyzed_tests="0",
                    total_tests="3",
                    url="https://azuredevops/project/run",
                ),
                dict(
                    key="4",
                    name="A",
                    state="Completed",
                    build_id="2",
                    started_date="",
                    completed_date="",
                    counted_tests="1",
                    incomplete_tests="0",
                    not_applicable_tests="0",
                    passed_tests="1",
                    unanalyzed_tests="0",
                    total_tests="1",
                    url="",
                ),
                dict(
                    key="6",
                    name="A+",
                    state="Completed",
                    build_id="1",
                    started_date="",
                    completed_date="",
                    counted_tests="6",
                    incomplete_tests="0",
                    not_applicable_tests="0",
                    passed_tests="6",
                    unanalyzed_tests="0",
                    total_tests="6",
                    url="",
                ),
            ],
        )

    async def test_nr_of_failed_tests(self):
        """Test that the number of failed tests is returned."""
        self.sources["source_id"]["test_result"] = ["failed"]
        metric = dict(type="tests", sources=self.sources, addition="sum")
        response = await self.collect(
            metric,
            get_request_json_return_value=dict(
                value=[dict(id="1", build=dict(id="1"), state="Completed", unanalyzedTests=4)]
            ),
        )
        self.assert_measurement(response, value="4")
