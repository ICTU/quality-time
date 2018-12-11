"""Test client for the Quality-time API."""

import asyncio
import json
import sys

import aiohttp


NON_EXISTING = "http://non-existing-hostname.io"
SONARQUBE = "http://sonarcloud.io"
JACOCO = "https://www.jacoco.org/jacoco/trunk/coverage/jacoco.xml"
JUNIT_TEST = "https://raw.githubusercontent.com/inorton/junit2html/master/junit2htmlreport/tests"
JUNIT_TEST2 = "https://raw.githubusercontent.com/notnoop/hudson-tools/master/toJunitXML/sample-junit.xml"

APIS = [
    f"tests/junit?url={JUNIT_TEST}/junit-complex_suites.xml&url={JUNIT_TEST}/junit-simple_suite.xml",
    f"failed_tests/junit?url={JUNIT_TEST}/junit-complex_suites.xml&url={JUNIT_TEST}/junit-simple_suite.xml",
    f"tests/junit?url={JUNIT_TEST2}",
    f"failed_tests/junit?url={JUNIT_TEST2}",
    f"covered_lines/jacoco?url={JACOCO}",
    f"uncovered_lines/jacoco?url={JACOCO}",
    f"covered_branches/jacoco?url={JACOCO}",
    f"uncovered_branches/jacoco?url={JACOCO}",
    f"tests/sonarqube?url={SONARQUBE}&component=fniessink:next-action",
    f"tests/sonarqube?url={SONARQUBE}&component=nl.ictu:hq",
    f"failed_tests/sonarqube?url={SONARQUBE}&component=fniessink:next-action",
    f"failed_tests/sonarqube?url={SONARQUBE}&component=nl.ictu:hq",
    f"covered_lines/sonarqube?url={SONARQUBE}&component=fniessink:next-action",
    f"covered_lines/sonarqube?url={SONARQUBE}&component=nl.ictu:hq",
    f"uncovered_lines/sonarqube?url={SONARQUBE}&component=fniessink:next-action",
    f"uncovered_lines/sonarqube?url={SONARQUBE}&component=nl.ictu:hq",
    f"covered_branches/sonarqube?url={SONARQUBE}&component=fniessink:next-action",
    f"covered_branches/sonarqube?url={SONARQUBE}&component=nl.ictu:hq",
    f"uncovered_branches/sonarqube?url={SONARQUBE}&component=fniessink:next-action",
    f"uncovered_branches/sonarqube?url={SONARQUBE}&component=nl.ictu:hq",
    f"loc/sonarqube?url={SONARQUBE}&component=fniessink:next-action",
    f"loc/sonarqube?url={SONARQUBE}&component=nl.ictu:hq",
    f"ncloc/sonarqube?url={SONARQUBE}&component=fniessink:next-action",
    f"ncloc/sonarqube?url={SONARQUBE}&component=nl.ictu:hq",
    f"violations/sonarqube?url={SONARQUBE}&component=fniessink:next-action",
    f"violations/sonarqube?url={SONARQUBE}&component=nl.ictu:hq",
    f"version/sonarqube?url={SONARQUBE}"]


async def fetch(api):
    """Fetch one APIs asynchronously."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://localhost:8080/{api}") as response:
            json_content = await response.json()
            print(json.dumps(json_content, indent="  "))


async def fetch_all(apis):
    """Fetch all APIs asynchronously."""
    await asyncio.gather(*(fetch(api) for api in apis))


def main():
    """Read, filter and fetch the APIs."""
    apis = APIS
    try:
        apis.extend([url.strip() for url in open(".urls.txt").readlines()])
    except FileNotFoundError:
        pass
    for filter_term in sys.argv[1:]:
        apis = [api for api in apis if filter_term in api]
    asyncio.run(fetch_all(apis))


if __name__ == "__main__":
    main()
