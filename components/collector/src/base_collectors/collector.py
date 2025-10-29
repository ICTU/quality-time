"""Metrics collector."""

import asyncio
import logging
import pathlib
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, NoReturn, cast

import aiohttp
from dateutil.tz import tzutc

from shared.database.reports import get_reports
from shared.model.report import get_metrics_from_reports

from collector_utilities.log import get_logger
from collector_utilities.type import JSONDict
from database.measurements import create_measurement

from . import config
from .metric_collector import MetricCollector

if TYPE_CHECKING:
    from pymongo.database import Database

    from shared.model.metric import Metric


class Collector:
    """Collect measurements for all metrics."""

    def __init__(self, database: Database) -> None:
        self.__previous_metrics: dict[str, Any] = {}
        self.next_fetch: dict[str, datetime] = {}
        self.database: Database = database
        self.running_tasks: set[asyncio.Task] = set()

    @staticmethod
    def record_health() -> None:
        """Record the current date and time in a file to allow for health checks."""
        logger = get_logger()
        filename = pathlib.Path(config.HEALTH_CHECK_FILE)
        try:
            with filename.open("w", encoding="utf-8") as health_check:
                health_check.write(datetime.now(tz=tzutc()).isoformat())
        except OSError as reason:
            logger.error("Could not write health check time stamp to %s: %s", filename, reason)  # noqa: TRY400

    async def start(self) -> NoReturn:
        """Start fetching measurements indefinitely."""
        # The TCPConnector has limit 0, meaning unlimited, because aiohttp only closes connections when the response
        # is closed. But due to the architecture of the collector (first collect all the responses, then parse them)
        # the responses are kept around relatively long, and hence the connections too. To prevent time-outs while
        # aiohttp waits for connections to become available we don't limit the connection pool size.
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=0, ssl=False),
            raise_for_status=True,
            timeout=aiohttp.ClientTimeout(total=config.MEASUREMENT_TIMEOUT),
            trust_env=True,
        ) as session:
            while True:
                self.__log_tasks("Waking up")
                self.record_health()
                self.collect_metrics(session)
                self.__log_tasks(f"Going to sleep for {config.SLEEP_DURATION} seconds", config.MEASUREMENT_LIMIT)
                await asyncio.sleep(config.SLEEP_DURATION)

    def collect_metrics(self, session: aiohttp.ClientSession) -> None:
        """Collect measurements for metrics, prioritizing edited metrics."""
        reports = get_reports(self.database)
        metrics = get_metrics_from_reports(reports)
        next_fetch = datetime.now(tz=tzutc()) + timedelta(seconds=config.MEASUREMENT_FREQUENCY)
        nr_created_tasks = 0
        for metric_uuid, metric in self.__sorted_by_edit_status(cast(JSONDict, metrics)):
            if not self.__should_collect(metric_uuid, metric):
                continue
            task = asyncio.create_task(self.collect_metric(session, metric_uuid, metric, next_fetch))
            self.running_tasks.add(task)  # Keep a reference to the task to prevent it from being garbage collected
            task.add_done_callback(self.running_tasks.discard)  # Remove the task from the running tasks when done
            nr_created_tasks += 1
            if nr_created_tasks >= config.MEASUREMENT_LIMIT:
                break

    async def collect_metric(
        self,
        session: aiohttp.ClientSession,
        metric_uuid: str,
        metric: Metric,
        next_fetch: datetime,
    ) -> None:
        """Collect measurements for the metric and add them to the database."""
        self.__previous_metrics[metric_uuid] = metric
        self.next_fetch[metric_uuid] = next_fetch
        metric_collector_class = MetricCollector.get_subclass(metric["type"])
        metric_collector = metric_collector_class(session, metric)
        if measurement := await metric_collector.collect():
            measurement.metric_uuid = metric_uuid
            measurement.report_uuid = metric["report_uuid"]
            create_measurement(self.database, measurement.as_dict())

    def __sorted_by_edit_status(self, metrics: JSONDict) -> list[tuple[str, Any]]:
        """First return the edited metrics, then the rest."""
        return sorted(metrics.items(), key=lambda item: bool(self.__previous_metrics.get(item[0]) == item[1]))

    def __should_collect(self, metric_uuid: str, metric: dict) -> bool:
        """Return whether the metric should be collected.

        Metric should be collected when the user changes the configuration or when it has been collected too long ago.
        """
        metric_edited = self.__previous_metrics.get(metric_uuid) != metric
        metric_due = self.next_fetch.get(metric_uuid, datetime.min.replace(tzinfo=tzutc())) <= datetime.now(tz=tzutc())
        return metric_edited or metric_due

    def __log_tasks(self, event: str, warning_threshold: int = 0) -> None:
        """Log the number of running tasks."""
        level = logging.WARNING if len(self.running_tasks) > warning_threshold else logging.INFO
        logger = get_logger()
        logger.log(level, "%s: %d task(s) currently running", event, len(self.running_tasks))
