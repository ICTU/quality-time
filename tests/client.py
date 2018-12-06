import aiohttp
import asyncio
import json
import requests
import sys

NON_EXISTING = "http://non-existing-hostname.io"
SONARQUBE = "http://sonarcloud.io"
JUNIT_TEST = "https://raw.githubusercontent.com/inorton/junit2html/master/junit2htmlreport/tests"
JUNIT_TEST2 = "https://raw.githubusercontent.com/notnoop/hudson-tools/master/toJunitXML/sample-junit.xml"

APIS_OLD = [
    f"sonarqube/{SONARQUBE}/m/ncloc/non-existing-id:non-existing-id",
    f"sonarqube/{NON_EXISTING}/m/critical_violations/nl.ictu:hq",
    f"junit/{NON_EXISTING}/m/failures",
    f"junit/{JUNIT_TEST}/junit-complex_suites.xml/m/failures",
    f"junit/{JUNIT_TEST}/junit-complex_suites.xml/m/tests",
    f"junit/{JUNIT_TEST}/junit-simple_suite.xml/m/failures",
    f"junit/{JUNIT_TEST}/junit-simple_suite.xml/m/tests",
    f"junit/{JUNIT_TEST}/junit-simple_suite.xml/m/skipped",
    f"sonarqube/{SONARQUBE}/m/ncloc/nl.ictu:hq",
    f"sonarqube/{SONARQUBE}/m/lines/nl.ictu:hq",
    f"sonarqube/{SONARQUBE}/m/major_violations/nl.ictu:hq",
    f"sonarqube/{SONARQUBE}/m/critical_violations/nl.ictu:hq",
    f"sonarqube/{SONARQUBE}/m/issues/nl.ictu:hq",
    f"sonarqube/{SONARQUBE}/m/version"]
    
APIS = [
    f"tests/junit?url={JUNIT_TEST}/junit-complex_suites.xml&url={JUNIT_TEST}/junit-simple_suite.xml",
    f"failed_tests/junit?url={JUNIT_TEST}/junit-complex_suites.xml&url={JUNIT_TEST}/junit-simple_suite.xml",
    f"tests/junit?url={JUNIT_TEST2}",
    f"failed_tests/junit?url={JUNIT_TEST2}",
    f"tests/sonarqube?url={SONARQUBE}&component=nl.ictu:hq",
    f"failed_tests/sonarqube?url={SONARQUBE}&component=nl.ictu:hq",
    f"ncloc/sonarqube?url={SONARQUBE}&component=nl.ictu:hq",
    f"tests/sonarqube?url={SONARQUBE}&component=fniessink:next-action",
    f"failed_tests/sonarqube?url={SONARQUBE}&component=fniessink:next-action",
    f"ncloc/sonarqube?url={SONARQUBE}&component=fniessink:next-action",
    f"version/sonarqube?url={SONARQUBE}"]
    

async def fetch(api):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://localhost:8080/{api}") as response:
            json_content = await response.json()
            print(json.dumps(json_content, indent="  "))


async def fetch_all(apis):
    await asyncio.gather(*(fetch(api) for api in apis))


if __name__ == "__main__":
    apis = APIS 
    try:
        apis.extend([url.strip() for url in open(".urls.txt").readlines()])
    except FileNotFoundError:
        pass
    apis = [api for api in APIS if sys.argv[1] in api] if len(sys.argv) > 1 else APIS
    asyncio.run(fetch_all(apis))
