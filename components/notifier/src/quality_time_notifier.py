"""Notifier."""

import asyncio
import logging
import os

import aiohttp
import pymsteams

from strategies.reds_per_report import reds_per_report


async def notify(log_level: int = None) -> None:
    """Notify our users."""
    logging.getLogger().setLevel(log_level or logging.ERROR)
    while True:
        async with aiohttp.ClientSession(raise_for_status=True, trust_env=True) as session:
            response = await session.get(
                f"http://{os.environ.get('SERVER_HOST', 'localhost')}:"
                f"{os.environ.get('SERVER_PORT', '5001')}/api/v3/reports")
            json = await response.json()

            reds_in_reports = reds_per_report(json)

            notification = "number of red metrics in each report:"
            for report in reds_in_reports:
                notification += "\n\r - " + report[0] + ": " + str(report[1])
            print(notification)

            my_teams_message = pymsteams.connectorcard(os.environ.get("TEAMS_WEBHOOK"))
            my_teams_message.text(notification)
            my_teams_message.send()

            await asyncio.sleep(int(os.environ.get('NOTIFIER_SLEEP_DURATION', 60)))


if __name__ == "__main__":
    asyncio.run(notify(logging.INFO))  # pragma: no cover
