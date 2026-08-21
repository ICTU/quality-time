"""Unit tests for the GitLab CI-pipelines collector."""

from .base import FakeResponse, GitLabTestCase

type Pipeline = dict[str, str | int]


class GitLabPipelinesTest(GitLabTestCase):
    """Unit tests for the CI-pipelines metric."""

    METRIC_TYPE = "pipelines"
    PIPELINES_LANDING_URL = "https://gitlab/namespace/project/-/pipelines"

    def setUp(self) -> None:
        """Extend to set up fixtures."""
        super().setUp()
        self.pipeline_schedules_json = [{"id": "pipeline schedule id", "description": "nightly"}]
        self.scheduled_pipelines_json = [{"id": 1}]
        # Pipelines as returned by the GitLab API, most recent first, see the example in the metric documentation
        self.pipelines_json = [
            self.create_pipeline(5, "main", "success", updated_at="2025-09-05T00:00:00.000Z"),
            self.create_pipeline(4, "main", "failed", updated_at="2025-09-04T00:00:00.000Z"),
            self.create_pipeline(3, "dev", "failed", updated_at="2025-09-03T00:00:00.000Z"),
            self.create_pipeline(2, "dev", "success", source="schedule", updated_at="2025-09-02T00:00:00.000Z"),
            self.create_pipeline(1, "main", "failed", source="schedule"),
        ]

    @staticmethod
    def create_pipeline(pipeline_id: int, ref: str = "main", status: str = "success", **kwargs: str) -> Pipeline:
        """Create a pipeline, as returned by the GitLab API to list the pipelines of a project."""
        pipeline: Pipeline = {
            "id": pipeline_id,
            "project_id": "project id",
            "name": f"Pipeline {pipeline_id}",
            "created_at": "2025-09-01T00:00:00.000Z",
            "updated_at": "2025-09-01T00:00:00.000Z",
            "ref": ref,
            "status": status,
            "source": "push",
            "web_url": f"https://gitlab/namespace/project/-/pipelines/{pipeline_id}",
        }
        return pipeline | kwargs

    @staticmethod
    def expected_entity(pipeline: Pipeline) -> dict[str, str]:
        """Return the entity expected for the pipeline."""
        return {
            "key": str(pipeline["id"]),
            "name": str(pipeline["name"]),
            "ref": str(pipeline["ref"]),
            "status": str(pipeline["status"]),
            "trigger": str(pipeline["source"]),
            "schedule": "nightly" if pipeline["id"] == 1 else "",
            "created": str(pipeline["created_at"]),
            "updated": str(pipeline["updated_at"]),
            "url": str(pipeline["web_url"]),
        }

    def expected_pipeline_entities(self, *pipeline_ids: int) -> list[dict[str, str]]:
        """Return the entities expected for the pipelines with the specified ids, in the order of the fixture."""
        return [self.expected_entity(pipeline) for pipeline in self.pipelines_json if pipeline["id"] in pipeline_ids]

    async def collect(self, **kwargs):
        """Override to pass the GitLab pipeline JSON responses."""
        responses = [
            FakeResponse(self.pipeline_schedules_json),  # To fetch all pipeline schedules
            FakeResponse(self.scheduled_pipelines_json),  # To fetch all pipelines for the pipeline schedule
            FakeResponse(self.pipelines_json),  # To fetch all pipelines
        ]
        return await super().collect(get_request_side_effect=responses, **kwargs)

    async def test_no_filters(self):
        """Test that all pipelines in the look-back period are counted."""
        measurement = await self.collect_measurement()
        self.assert_measurement(
            measurement,
            value="5",
            total="5",
            entities=self.expected_pipeline_entities(5, 4, 3, 2, 1),
            landing_url=self.PIPELINES_LANDING_URL,
        )

    async def test_no_pipelines(self):
        """Test that zero pipelines is not an error."""
        self.pipelines_json = []
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, value="0", total="0", entities=[], landing_url=self.PIPELINES_LANDING_URL)

    async def test_filter_by_status(self):
        """Test that pipelines can be filtered by status."""
        self.set_source_parameter("pipeline_statuses_to_include", ["failed"])
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, value="3", total="5", entities=self.expected_pipeline_entities(4, 3, 1))

    async def test_filter_by_branch(self):
        """Test that pipelines can be filtered by branch."""
        self.set_source_parameter("branches", ["main"])
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, value="3", total="5", entities=self.expected_pipeline_entities(5, 4, 1))

    async def test_filter_by_trigger(self):
        """Test that pipelines can be filtered by trigger."""
        self.set_source_parameter("pipeline_triggers_to_include", ["schedule"])
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, value="2", total="5", entities=self.expected_pipeline_entities(2, 1))

    async def test_filter_by_schedule(self):
        """Test that pipelines can be filtered by pipeline schedule description."""
        self.set_source_parameter("pipeline_schedules_to_include", ["nightly"])
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, value="1", total="5", entities=self.expected_pipeline_entities(1))

    async def test_most_recent_pipeline_per_branch_did_not_fail(self):
        """Test that the most recent pipeline of the branch is selected before the status filter is applied.

        Pipeline 5, the most recent pipeline of the branch main, succeeded, so even though older pipelines of main
        did fail, the value is zero.
        """
        self.set_source_parameter("branches", ["main"])
        self.set_source_parameter("pipeline_statuses_to_include", ["failed"])
        self.set_source_parameter("only_include_most_recent_pipeline_per_branch", "yes")
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, value="0", total="1", entities=[])

    async def test_most_recent_pipeline_per_branch_failed(self):
        """Test that the metric reports one pipeline if the most recent pipeline of the branch failed."""
        self.pipelines_json.remove(self.pipelines_json[0])  # Remove pipeline 5, so pipeline 4 is the most recent
        self.set_source_parameter("branches", ["main"])
        self.set_source_parameter("pipeline_statuses_to_include", ["failed"])
        self.set_source_parameter("only_include_most_recent_pipeline_per_branch", "yes")
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, value="1", total="1", entities=self.expected_pipeline_entities(4))

    async def test_most_recent_pipeline_per_branch_succeeded(self):
        """Test that the most recent pipeline of the branch can also be filtered by a positive status."""
        self.set_source_parameter("branches", ["main"])
        self.set_source_parameter("pipeline_statuses_to_include", ["success"])
        self.set_source_parameter("only_include_most_recent_pipeline_per_branch", "yes")
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, value="1", total="1", entities=self.expected_pipeline_entities(5))

    async def test_most_recent_pipeline_of_multiple_branches(self):
        """Test that the most recent pipeline of each branch is selected when no branches are specified."""
        self.set_source_parameter("pipeline_statuses_to_include", ["failed"])
        self.set_source_parameter("only_include_most_recent_pipeline_per_branch", "yes")
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, value="1", total="2", entities=self.expected_pipeline_entities(3))

    async def test_most_recent_pipeline_of_multiple_branches_without_status_filter(self):
        """Test that the most recent pipeline of each branch is counted when no statuses are specified."""
        self.set_source_parameter("only_include_most_recent_pipeline_per_branch", "yes")
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, value="2", total="2", entities=self.expected_pipeline_entities(5, 3))

    async def test_selection_filters_applied_before_most_recent_pipeline_is_selected(self):
        """Test that the trigger filter is applied before the most recent pipeline of each branch is selected."""
        self.set_source_parameter("branches", ["main"])
        self.set_source_parameter("pipeline_triggers_to_include", ["schedule"])
        self.set_source_parameter("pipeline_statuses_to_include", ["failed"])
        self.set_source_parameter("only_include_most_recent_pipeline_per_branch", "yes")
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, value="1", total="1", entities=self.expected_pipeline_entities(1))

    async def test_pipeline_without_updated_datetime(self):
        """Test that the created datetime is used when the pipeline has no updated datetime."""
        del self.pipelines_json[0]["updated_at"]  # Pipeline 5 was created before pipeline 4 was updated
        self.set_source_parameter("branches", ["main"])
        self.set_source_parameter("only_include_most_recent_pipeline_per_branch", "yes")
        measurement = await self.collect_measurement()
        expected_entities = self.expected_pipeline_entities(4)
        self.assert_measurement(measurement, value="1", total="1", entities=expected_entities)

    async def test_pipelines_with_equal_datetimes(self):
        """Test that the pipeline with the highest id wins when two pipelines have the same datetime."""
        self.pipelines_json = [
            self.create_pipeline(6, "main", "failed", updated_at="2025-09-06T00:00:00.000Z"),
            self.create_pipeline(7, "main", "success", updated_at="2025-09-06T00:00:00.000Z"),
        ]
        self.set_source_parameter("pipeline_statuses_to_include", ["success"])
        self.set_source_parameter("only_include_most_recent_pipeline_per_branch", "yes")
        measurement = await self.collect_measurement()
        self.assert_measurement(measurement, value="1", total="1", entities=self.expected_pipeline_entities(7))
