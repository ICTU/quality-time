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
from collector_utilities.type import JSON, URL

from .source_collector import SourceCollector


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


class MetricsCollector:
    """Collect measurements for all metrics."""

    API_VERSION = "v3"
    MAX_SLEEP_DURATION = int(os.environ.get("COLLECTOR_SLEEP_DURATION", 20))
    MEASUREMENT_LIMIT = int(os.environ.get("COLLECTOR_MEASUREMENT_LIMIT", 30))
    MEASUREMENT_FREQUENCY = int(os.environ.get("COLLECTOR_MEASUREMENT_FREQUENCY", 15 * 60))

    def __init__(self) -> None:
        self.server_url: Final[URL] = URL(
            f"http://{os.environ.get('SERVER_HOST', 'localhost')}:{os.environ.get('SERVER_PORT', '5001')}"
        )
        self.data_model: JSON = {}
        self.last_parameters: dict[str, Any] = {}
        self.next_fetch: dict[str, datetime] = {}

    @staticmethod
    def record_health(filename: str = "/home/collector/health_check.txt") -> None:
        """Record the current date and time in a file to allow for health checks."""
        try:
            with open(filename, "w") as health_check:
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

    async def fetch_data_model(self, session: aiohttp.ClientSession) -> JSON:
        """Fetch the data model."""
        # The first attempt is likely to fail because the collector starts up faster than the server,
        # so don't log tracebacks on the first attempt
        first_attempt = True
        data_model_url = URL(f"{self.server_url}/api/{self.API_VERSION}/datamodel")
        while True:
            self.record_health()
            logging.info("Loading data model from %s...", data_model_url)
            if data_model := await get(session, data_model_url, log=not first_attempt):
                return data_model
            first_attempt = False
            logging.warning("Loading data model failed, trying again in %ss...", self.MAX_SLEEP_DURATION)
            await asyncio.sleep(self.MAX_SLEEP_DURATION)

    async def collect_metrics(self, session: aiohttp.ClientSession) -> None:
        """Collect measurements for all metrics."""
        metrics = await get(session, URL(f"{self.server_url}/internal-api/{self.API_VERSION}/metrics"))
        next_fetch = datetime.now() + timedelta(seconds=self.MEASUREMENT_FREQUENCY)
        tasks: list[Coroutine] = []
        for metric_uuid, metric in metrics.items():
            if len(tasks) >= self.MEASUREMENT_LIMIT:
                break
            if self.__can_and_should_collect(metric_uuid, metric):
                tasks.append(self.collect_metric(session, metric_uuid, metric, next_fetch))
        await asyncio.gather(*tasks)

    async def collect_metric(self, session: aiohttp.ClientSession, metric_uuid, metric, next_fetch: datetime) -> None:
        """Collect measurements for the metric and post it to the server."""
        self.last_parameters[metric_uuid] = metric
        self.next_fetch[metric_uuid] = next_fetch
        if measurement := await self.collect_sources(session, metric):
            measurement["metric_uuid"] = metric_uuid
            await post(session, URL(f"{self.server_url}/internal-api/{self.API_VERSION}/measurements"), measurement)

    async def collect_sources(self, session: aiohttp.ClientSession, metric):
        """Collect the measurements from the metric's sources."""
        collectors = []
        for source in metric["sources"].values():
            if collector_class := SourceCollector.get_subclass(source["type"], metric["type"]):
                collectors.append(collector_class(session, source, self.data_model).get())
        if not collectors:
            return
        measurements = await asyncio.gather(*collectors)
        has_error = False
        for measurement, source_uuid in zip(measurements, metric["sources"]):
            measurement["source_uuid"] = source_uuid
            has_error = True if bool(measurement["connection_error"] or measurement["parse_error"]) else has_error
        return dict(has_error=has_error, sources=measurements)

    def __can_and_should_collect(self, metric_uuid: str, metric) -> bool:
        """Return whether the metric can and needs to be measured."""
        return self.__should_collect(metric_uuid, metric) if self.__can_collect(metric) else False

    def __can_collect(self, metric) -> bool:
        """Return whether the user has specified all mandatory parameters for all sources."""
        sources = metric.get("sources")
        for source in sources.values():
            parameters = self.data_model.get("sources", {}).get(source["type"], {}).get("parameters", {})
            for parameter_key, parameter in parameters.items():
                if (
                    parameter.get("mandatory")
                    and metric["type"] in parameter.get("metrics")
                    and not source.get("parameters", {}).get(parameter_key)
                    and not parameter.get("default_value")
                ):
                    return False
        return bool(sources)

    def __should_collect(self, metric_uuid: str, metric) -> bool:
        """Return whether the metric should be collected.

        Metric should be collected when the user changes the configuration or when it has been collected too long ago.
        """
        metric_changed = self.last_parameters.get(metric_uuid) != metric
        metric_due = self.next_fetch.get(metric_uuid, datetime.min) <= datetime.now()
        return metric_changed or metric_due
