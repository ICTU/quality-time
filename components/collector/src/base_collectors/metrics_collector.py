"""Metrics collector."""

from datetime import datetime, timedelta
import asyncio
import logging
import os
import traceback
from typing import cast, Any, Dict, Final, NoReturn

import aiohttp

from collector_utilities.functions import timer
from collector_utilities.type import JSON, URL
from .source_collector import SourceCollector


async def get(session: aiohttp.ClientSession, api: URL) -> JSON:
    """Get data from the API url."""
    try:
        response = await session.get(api)
        return cast(JSON, await response.json())
    except Exception as reason:  # pylint: disable=broad-except
        logging.error("Getting data from %s failed: %s", api, reason)
        logging.error(traceback.format_exc())
        return {}


async def post(session: aiohttp.ClientSession, api: URL, data) -> None:
    """Post the JSON data to the api url."""
    try:
        await session.post(api, json=data)
    except Exception as reason:  # pylint: disable=broad-except
        logging.error("Posting %s to %s failed: %s", data, api, reason)
        logging.error(traceback.format_exc())


class MetricsCollector:
    """Collect measurements for all metrics."""
    def __init__(self) -> None:
        self.server_url: Final[URL] = \
            URL(f"http://{os.environ.get('SERVER_HOST', 'localhost')}:{os.environ.get('SERVER_PORT', '5001')}")
        self.data_model: JSON = dict()
        self.next_fetch: Dict[str, datetime] = dict()
        self.last_parameters: Dict[str, Any] = dict()

    @staticmethod
    def record_health(filename: str = "/tmp/health_check.txt") -> None:
        """Record the current date and time in a file to allow for health checks."""
        try:
            with open(filename, "w") as health_check:
                health_check.write(datetime.now().isoformat())
        except OSError as reason:
            logging.error("Could not write health check time stamp to %s: %s", filename, reason)

    async def start(self) -> NoReturn:
        """Start fetching measurements indefinitely."""
        max_sleep_duration = int(os.environ.get("COLLECTOR_SLEEP_DURATION", 60))
        measurement_frequency = int(os.environ.get("COLLECTOR_MEASUREMENT_FREQUENCY", 15 * 60))
        timeout = aiohttp.ClientTimeout(total=120)
        async with aiohttp.ClientSession(timeout=timeout, raise_for_status=True) as session:
            self.data_model = await self.fetch_data_model(session, max_sleep_duration)
        while True:
            self.record_health()
            logging.info("Collecting...")
            async with aiohttp.ClientSession(
                    timeout=timeout, connector=aiohttp.TCPConnector(limit_per_host=20),
                    raise_for_status=True) as session:
                with timer() as collection_timer:
                    await self.collect_metrics(session, measurement_frequency)
            sleep_duration = max(0, max_sleep_duration - collection_timer.duration)
            logging.info(
                "Collecting took %.1f seconds. Sleeping %.1f seconds...", collection_timer.duration, sleep_duration)
            await asyncio.sleep(sleep_duration)

    async def fetch_data_model(self, session: aiohttp.ClientSession, sleep_duration: int) -> JSON:
        """Fetch the data model."""
        while True:
            self.record_health()
            logging.info("Loading data model...")
            if data_model := await get(session, URL(f"{self.server_url}/api/v2/datamodel")):
                return data_model
            logging.warning("Loading data model failed, trying again in %ss...", sleep_duration)
            await asyncio.sleep(sleep_duration)

    async def collect_metrics(self, session: aiohttp.ClientSession, measurement_frequency: int) -> None:
        """Collect measurements for all metrics."""
        metrics = await get(session, URL(f"{self.server_url}/api/v2/metrics"))
        next_fetch = datetime.now() + timedelta(seconds=measurement_frequency)
        tasks = [self.collect_metric(session, metric_uuid, metric, next_fetch)
                 for metric_uuid, metric in metrics.items() if self.__can_and_should_collect(metric_uuid, metric)]
        await asyncio.gather(*tasks)

    async def collect_metric(
            self, session: aiohttp.ClientSession, metric_uuid, metric, next_fetch: datetime) -> None:
        """Collect measurements for the metric and post it to the server."""
        self.last_parameters[metric_uuid] = metric
        self.next_fetch[metric_uuid] = next_fetch
        measurement = await self.collect_sources(session, metric)
        measurement["metric_uuid"] = metric_uuid
        await post(session, URL(f"{self.server_url}/api/v2/measurements"), measurement)

    async def collect_sources(self, session: aiohttp.ClientSession, metric):
        """Collect the measurements from the metric's sources."""
        collectors = []
        for source in metric["sources"].values():
            collector_class = SourceCollector.get_subclass(source["type"], metric["type"])
            collectors.append(collector_class(session, source, self.data_model).get())
        measurements = await asyncio.gather(*collectors)
        for measurement, source_uuid in zip(measurements, metric["sources"]):
            measurement["source_uuid"] = source_uuid
        return dict(sources=measurements)

    def __can_and_should_collect(self, metric_uuid: str, metric) -> bool:
        """Return whether the metric can and needs to be measured."""
        if not self.__can_collect(metric):
            return False
        return self.__should_collect(metric_uuid, metric)

    def __can_collect(self, metric) -> bool:
        """Return whether the user has specified all mandatory parameters for all sources."""
        sources = metric.get("sources")
        for source in sources.values():
            parameters = self.data_model.get("sources", {}).get(source["type"], {}).get("parameters", {})
            for parameter_key, parameter in parameters.items():
                if parameter.get("mandatory") and metric["type"] in parameter.get("metrics") and \
                        not source.get("parameters", {}).get(parameter_key):
                    return False
        return bool(sources)

    def __should_collect(self, metric_uuid: str, metric) -> bool:
        """Return whether the metric should be collected, either because the user changed the configuration or because
        it has been collected too long ago."""
        if self.last_parameters.get(metric_uuid) != metric:
            return True
        return self.next_fetch.get(metric_uuid, datetime.min) <= datetime.now()
