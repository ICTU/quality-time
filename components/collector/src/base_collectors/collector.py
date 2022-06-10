"""Metrics collector."""

import asyncio
import logging
import os
import time
import traceback
from datetime import datetime, timedelta
from typing import Any, Coroutine, Final, NoReturn, cast

import aiohttp

from collector_utilities.functions import timer
from collector_utilities.type import JSON, JSONDict, URL

from .metric_collector import MetricCollector


async def get(session: aiohttp.ClientSession, api: URL, log: bool = True) -> JSON:
    """Get data from the API url."""
    try:
        response = await session.get(api)
        json = cast(JSON, await response.json())
        response.close()
        return json
    except Exception as reason:  # pylint: disable=broad-except
        if log:
            logging.error("Getting data from %s failed: %s", api, reason)
            logging.error(traceback.format_exc())
        return {}


async def post(session: aiohttp.ClientSession, api: URL, data) -> None:
    """Post the JSON data to the api url."""
    start = time.time()
    text_data = str(data)
    try:
        response = await session.post(api, json=data)
        response.close()
    except Exception as reason:  # pylint: disable=broad-except
        logging.error("Posting %s to %s failed: %s", data, api, reason)
        logging.error(traceback.format_exc())
    finally:
        if time.time() - start > 10:  # pragma: no cover
            logging.info("Posting to %s. Length = %d. First 1000 chars = %s", api, len(text_data), text_data[:1000])


class Collector:
    """Collect measurements for all metrics."""

    MAX_SLEEP_DURATION = int(os.environ.get("COLLECTOR_SLEEP_DURATION", 20))
    MEASUREMENT_LIMIT = int(os.environ.get("COLLECTOR_MEASUREMENT_LIMIT", 30))
    MEASUREMENT_FREQUENCY = int(os.environ.get("COLLECTOR_MEASUREMENT_FREQUENCY", 15 * 60))

    def __init__(self) -> None:
        internal_server_host = os.environ.get("INTERNAL_SERVER_HOST", "localhost")
        internal_server_port = os.environ.get("INTERNAL_SERVER_PORT", "5002")
        self.server_url: Final[URL] = URL(f"http://{internal_server_host}:{internal_server_port}")
        self.data_model: JSONDict = {}
        self.__previous_metrics: dict[str, Any] = {}
        self.next_fetch: dict[str, datetime] = {}

    @staticmethod
    def record_health(filename: str = "/home/collector/health_check.txt") -> None:
        """Record the current date and time in a file to allow for health checks."""
        try:
            with open(filename, "w", encoding="utf-8") as health_check:
                health_check.write(datetime.now().isoformat())
        except OSError as reason:
            logging.error("Could not write health check time stamp to %s: %s", filename, reason)

    async def start(self) -> NoReturn:
        """Start fetching measurements indefinitely."""
        timeout = aiohttp.ClientTimeout(total=120)
        async with aiohttp.ClientSession(raise_for_status=True, timeout=timeout, trust_env=True) as session:
            self.data_model = await self.fetch_data_model(session)
        while True:
            self.record_health()
            # The TCPConnector has limit 0, meaning unlimited, because aiohttp only closes connections when the response
            # is closed. But due to the architecture of the collector (first collect all the responses, then parse them)
            # the responses are kept around relatively long, and hence the connections too. To prevent time-outs while
            # aiohttp waits for connections to become available we don't limit the connection pool size.
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=0, ssl=False),
                raise_for_status=True,
                timeout=timeout,
                trust_env=True,
            ) as session:
                with timer() as collection_timer:
                    await self.collect_metrics(session)
            sleep_duration = max(0, self.MAX_SLEEP_DURATION - collection_timer.duration)
            logging.info(
                "Collecting took %.1f seconds. Sleeping %.1f seconds...", collection_timer.duration, sleep_duration
            )
            await asyncio.sleep(sleep_duration)

    async def fetch_data_model(self, session: aiohttp.ClientSession) -> JSONDict:
        """Fetch the data model."""
        # The first attempt is likely to fail because the collector starts up faster than the server,
        # so don't log tracebacks on the first attempt
        first_attempt = True
        data_model_url = URL(f"{self.server_url}/api/datamodel")
        while True:
            self.record_health()
            logging.info("Loading data model from %s...", data_model_url)
            if data_model := await get(session, data_model_url, log=not first_attempt):
                return cast(JSONDict, data_model)
            first_attempt = False
            logging.warning("Loading data model failed, trying again in %ss...", self.MAX_SLEEP_DURATION)
            await asyncio.sleep(self.MAX_SLEEP_DURATION)

    async def collect_metrics(self, session: aiohttp.ClientSession) -> None:
        """Collect measurements for metrics, prioritizing edited metrics."""
        metrics = await get(session, URL(f"{self.server_url}/api/metrics"))
        next_fetch = datetime.now() + timedelta(seconds=self.MEASUREMENT_FREQUENCY)
        tasks: list[Coroutine] = []
        for metric_uuid, metric in self.__sorted_by_edit_status(cast(JSONDict, metrics)):
            if len(tasks) >= self.MEASUREMENT_LIMIT:
                break
            if self.__should_collect(metric_uuid, metric):
                tasks.append(self.collect_metric(session, metric_uuid, metric, next_fetch))
        await asyncio.gather(*tasks)

    async def collect_metric(
        self, session: aiohttp.ClientSession, metric_uuid: str, metric: dict, next_fetch: datetime
    ) -> None:
        """Collect measurements for the metric and post it to the server."""
        self.__previous_metrics[metric_uuid] = metric
        self.next_fetch[metric_uuid] = next_fetch
        metric_collector_class = MetricCollector.get_subclass(metric["type"])
        metric_collector = metric_collector_class(session, metric, self.data_model)
        if measurement := await metric_collector.collect():
            measurement.metric_uuid = metric_uuid
            measurement.report_uuid = metric["report_uuid"]
            api_url = URL(f"{self.server_url}/api/measurements")
            await post(session, api_url, measurement.as_dict())

    def __sorted_by_edit_status(self, metrics: JSONDict) -> list[tuple[str, Any]]:
        """First return the edited metrics, then the rest."""
        return sorted(metrics.items(), key=lambda item: bool(self.__previous_metrics.get(item[0]) == item[1]))

    def __should_collect(self, metric_uuid: str, metric: dict) -> bool:
        """Return whether the metric should be collected.

        Metric should be collected when the user changes the configuration or when it has been collected too long ago.
        """
        metric_edited = self.__previous_metrics.get(metric_uuid) != metric
        metric_due = self.next_fetch.get(metric_uuid, datetime.min) <= datetime.now()
        return metric_edited or metric_due
