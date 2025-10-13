"""Unit tests for the change failure rate metric collector."""

import unittest
from copy import deepcopy
from datetime import datetime, timedelta
from typing import ClassVar
from unittest.mock import AsyncMock, patch

from dateutil.tz import tzlocal, tzutc

from shared.model.metric import Metric

from base_collectors import config
from base_collectors.metric_collector import MetricCollector
from model import MetricMeasurement
from source_collectors.jira.change_failure_rate import JiraChangeFailureRate

from tests.fixtures import METRIC_ID


class ChangeFailureRateTest(unittest.IsolatedAsyncioTestCase):
    """Unit tests for the change failure rate metric collector."""

    EARLY_DT: datetime = datetime(2020, 8, 6, 8, 36, 48, 927000, tzinfo=tzlocal())
    DEPLOY_DT: datetime = EARLY_DT + timedelta(hours=2)
    ISSUE_DT: datetime = EARLY_DT + timedelta(hours=5)
    COLLECT_DT: datetime = EARLY_DT + timedelta(hours=9)

    GITLAB_JOBS_JSON: ClassVar[list[dict]] = [
        {
            "id": "1",
            "status": "failed",
            "name": "job1",
            "stage": "stage",
            "created_at": DEPLOY_DT.astimezone(tzutc()).isoformat().replace(".927000+00:00", ".007Z"),
            "finished_at": DEPLOY_DT.astimezone(tzutc()).isoformat().replace(".927000+00:00", ".927Z"),
            "pipeline": {"web_url": "https://gitlab/project/-/pipelines/1"},
            "web_url": "https://gitlab/job1",
            "ref": "main",
        },
    ]
    JENKINS_JOBS_JSON: ClassVar[dict[str, list[dict]]] = {
        "jobs": [
            {
                "name": "job",
                "url": "https://jenkins/job",
                "buildable": True,
                "color": "blue",
                "builds": [
                    {"result": "SUCCESS", "timestamp": int(datetime.timestamp(DEPLOY_DT)) * 1000},
                ],
            },
        ],
    }
    JIRA_CREATED: str = ISSUE_DT.isoformat()
    JIRA_SERVER_INFO: ClassVar[dict] = {}

    def setUp(self) -> None:
        """Extend to set up test fixtures."""
        super().setUp()
        self.session = AsyncMock()
        self.session.timeout.total = config.MEASUREMENT_TIMEOUT
        self.response = self.session.get.return_value = AsyncMock()
        self.response.json = AsyncMock()
        self.response.links = {}  # unset for pagination lookup

        self.gitlab_url = "https://gitlab"
        self.jenkins_url = "https://jenkins"
        self.jira_url = "https://jira"
        self.tickets_json = {"total": 1, "issues": [self.jira_issue()]}
        self.gitlab_source_config = {
            "type": "gitlab",
            "parameters": {"url": self.gitlab_url, "project": "project", "lookback_days": "100000"},
        }
        self.jenkins_source_config = {"type": "jenkins", "parameters": {"url": self.jenkins_url}}
        self.jira_source_config = {"type": "jira", "parameters": {"url": self.jira_url, "jql": "jql"}}

    def jira_issue(self, key: str = "key-1", **fields):
        """Create a Jira issue."""
        return {"id": key, "key": key, "fields": dict(created=self.JIRA_CREATED, summary=f"Summary {key}", **fields)}

    def jira_entity(self, key: str = "key-1"):
        """Create a Jira entity."""
        return {
            "key": key,
            "issue_key": key,
            "summary": f"Summary {key}",
            "url": f"{self.jira_url}/browse/{key}",
            "created": self.JIRA_CREATED,
            "updated": None,
            "status": None,
            "priority": None,
            "type": "Unknown issue type",
        }

    def gitlab_entity(self, job: str = "job1"):
        """Create a GitLab entity."""
        return {
            "branch": "main",
            "build_date": self.DEPLOY_DT.astimezone(tzutc()).date().isoformat(),
            "build_datetime": self.DEPLOY_DT,
            "build_result": "failed",
            "failed": True,
            "key": "1",
            "name": job,
            "stage": "stage",
            "url": f"{self.gitlab_url}/{job}",
        }

    def assert_entity(self, expected, actual):
        """Assert that the actual entity is contained within the expected entity."""
        del actual["first_seen"]  # always ignore first_seen
        self.assertEqual(expected, expected | actual)

    async def collect(self, sources) -> MetricMeasurement | None:
        """Collect the measurement."""
        side_effects = list(deepcopy(self.response.json.side_effect)) if self.response.json.side_effect else []
        metric = Metric({}, {"type": "change_failure_rate", "sources": sources}, METRIC_ID)
        # Instead of instantiating the ChangeFailureRate collector directly, we look up the collector by the metric type
        # to get full coverage. Note that the order of response.json.side_effects is important, due to mixed async calls
        change_failure_rate_collector_class = MetricCollector.get_subclass(metric["type"])
        with (
            patch.object(JiraChangeFailureRate, "max_results", 500),
            patch(
                "collector_utilities.date_time.datetime",
                wraps=datetime,
            ) as mock_dt,
        ):
            mock_dt.now.return_value = self.COLLECT_DT  # this shifts the perspective of `days_ago`
            measurement = await change_failure_rate_collector_class(self.session, metric).collect()

        if side_effects:
            self.assertEqual(len(side_effects), self.response.json.call_count)
        if measurement:
            self.assertFalse(measurement.has_error)
            for source in measurement.sources:
                self.assertIsNone(source.connection_error)
                self.assertIsNone(source.parse_error)
        return measurement

    async def test_no_sources(self):
        """Test metric collection, when there are no sources configured."""
        measurement = await self.collect({})
        self.assertIsNone(measurement)

    async def test_missing_issue_sources(self):
        """Test metric collection, when there are no issue sources configured."""
        self.response.json.side_effect = [
            self.GITLAB_JOBS_JSON,
            self.GITLAB_JOBS_JSON,
            self.JENKINS_JOBS_JSON,
        ]
        measurement = await self.collect({"gitlab": self.gitlab_source_config, "jenkins": self.jenkins_source_config})

        # both sources collected one job (total), but it is neither included as entity nor counted in value
        self.assertEqual([], measurement.sources[0].entities)
        self.assertEqual([], measurement.sources[1].entities)
        self.assertEqual("0", measurement.sources[0].value)
        self.assertEqual("0", measurement.sources[1].value)
        self.assertEqual("1", measurement.sources[0].total)
        self.assertEqual("1", measurement.sources[1].total)

    async def test_missing_deployment_sources(self):
        """Test metric collection, when there are no deployment sources configured."""
        self.response.json.side_effect = [
            [],
            self.JIRA_SERVER_INFO,
            self.tickets_json,
            self.tickets_json,
        ]
        measurement = await self.collect({"jira": self.jira_source_config})

        # there is one entity, but it is neither counted in value nor total
        self.assertEqual(1, len(measurement.sources[0].entities))
        self.assertEqual("0", measurement.sources[0].value)
        self.assertEqual("0", measurement.sources[0].total)
        self.assert_entity(self.jira_entity(), measurement.sources[0].entities[0])

    async def test_excluded_entity(self):
        """Test that metric collection correctly excludes entities."""
        self.response.json.side_effect = [
            self.JENKINS_JOBS_JSON,
            [],
            self.JIRA_SERVER_INFO,
            self.tickets_json,
            self.tickets_json,
        ]
        self.jenkins_source_config["parameters"]["jobs_to_include"] = ["nothing"]
        measurement = await self.collect({"jenkins": self.jenkins_source_config, "jira": self.jira_source_config})

        # jenkins collected one job (total), but it is neither included as entity nor counted in value
        self.assertEqual([], measurement.sources[0].entities)
        self.assertEqual("0", measurement.sources[0].total)
        self.assertEqual("0", measurement.sources[0].value)

        # jira has one entity, but neither value nor total is counted
        self.assertEqual(1, len(measurement.sources[1].entities))
        self.assertEqual("0", measurement.sources[1].total)
        self.assertEqual("0", measurement.sources[1].value)
        self.assert_entity(self.jira_entity(), measurement.sources[1].entities[0])

    async def test_only_match_issue_after_deploy(self):
        """Test that issues are not matched to deployments that were done later."""
        self.tickets_json["issues"][0]["fields"]["created"] = self.EARLY_DT.isoformat()
        self.response.json.side_effect = [
            self.JENKINS_JOBS_JSON,
            [],
            self.JIRA_SERVER_INFO,
            self.tickets_json,
            self.tickets_json,
        ]
        measurement = await self.collect({"jenkins": self.jenkins_source_config, "jira": self.jira_source_config})

        # jenkins collected one job (total), but it is neither included as entity nor counted in value
        self.assertEqual([], measurement.sources[0].entities)
        self.assertEqual("1", measurement.sources[0].total)
        self.assertEqual("0", measurement.sources[0].value)

        # jira has one entity, but neither value nor total is counted
        self.assertEqual(1, len(measurement.sources[1].entities))
        self.assertEqual("0", measurement.sources[1].total)
        self.assertEqual("0", measurement.sources[1].value)

        entity = measurement.sources[1].entities[0]
        del entity["created"]
        self.assert_entity(self.jira_entity(), entity)

    async def test_single_entity(self):
        """Test one deploy with issue ticket."""
        self.response.json.side_effect = [
            self.GITLAB_JOBS_JSON,
            self.GITLAB_JOBS_JSON,
            self.GITLAB_JOBS_JSON,
            self.JIRA_SERVER_INFO,
            self.tickets_json,
            self.tickets_json,
        ]
        measurement = await self.collect({"gitlab": self.gitlab_source_config, "jira": self.jira_source_config})

        # gitlab collected one job (total), which is included as entity and counted both in value and total
        self.assertEqual(1, len(measurement.sources[0].entities))
        self.assertEqual("1", measurement.sources[0].value)
        self.assertEqual("1", measurement.sources[0].total)

        # jira has one entity, but neither value nor total is counted
        self.assertEqual(1, len(measurement.sources[1].entities))
        self.assertEqual("0", measurement.sources[1].value)
        self.assertEqual("0", measurement.sources[1].total)

        self.assert_entity(self.gitlab_entity(), measurement.sources[0].entities[0])
        self.assert_entity(self.jira_entity(), measurement.sources[1].entities[0])
