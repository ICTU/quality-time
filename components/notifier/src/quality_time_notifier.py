"""Notifier."""

import asyncio
import logging
import os

import aiohttp


async def notify(log_level: int = None) -> None:
    """Notify our users."""
    logging.getLogger().setLevel(log_level or logging.ERROR)
    while True:
        async with aiohttp.ClientSession(raise_for_status=True, trust_env=True) as session:
            response = await session.get(
                f"http://{os.environ.get('SERVER_HOST', 'localhost')}:"
                f"{os.environ.get('SERVER_PORT', '5001')}/api/v3/reports")
            json = await response.json()
            red_metrics = 0
            for report in json["reports"]:
                for subject in report["subjects"].values():
                    for metric in subject["metrics"].values():
                        print(metric["status"], flush=True)
                        if metric["status"] == "target_met":
                            red_metrics = red_metrics + 1

            print(red_metrics, flush=True)
            await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(notify(logging.INFO))  # pragma: no cover
