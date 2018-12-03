import aiohttp
import asyncio
import json
import requests


urls = [
    "http://localhost:8080/sonarqube/http://sonarcloud.io/m/ncloc/non-existing-id:non-existing-id",
    "http://localhost:8080/sonarqube/http://non-existing-hostname.io/m/critical_violations/nl.ictu:hq",
    "http://localhost:8080/junit/http://non-existing-hostname.io/m/failures",
    "http://localhost:8080/junit/https://raw.githubusercontent.com/inorton/junit2html/master/junit2htmlreport/tests/junit-complex_suites.xml/m/failures",
    "http://localhost:8080/junit/https://raw.githubusercontent.com/inorton/junit2html/master/junit2htmlreport/tests/junit-complex_suites.xml/m/tests",
    "http://localhost:8080/junit/https://raw.githubusercontent.com/inorton/junit2html/master/junit2htmlreport/tests/junit-simple_suite.xml/m/failures",
    "http://localhost:8080/junit/https://raw.githubusercontent.com/inorton/junit2html/master/junit2htmlreport/tests/junit-simple_suite.xml/m/tests",
    "http://localhost:8080/junit/https://raw.githubusercontent.com/inorton/junit2html/master/junit2htmlreport/tests/junit-simple_suite.xml/m/skipped",
    "http://localhost:8080/sonarqube/http://sonarcloud.io/m/ncloc/nl.ictu:hq",
    "http://localhost:8080/sonarqube/http://sonarcloud.io/m/lines/nl.ictu:hq",
    "http://localhost:8080/sonarqube/http://sonarcloud.io/m/major_violations/nl.ictu:hq",
    "http://localhost:8080/sonarqube/http://sonarcloud.io/m/critical_violations/nl.ictu:hq",
    "http://localhost:8080/sonarqube/http://sonarcloud.io/m/issues/nl.ictu:hq",
    "http://localhost:8080/sonarqube/http://sonarcloud.io/m/version"]


async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            json_content = await response.json()
            print(json.dumps(json_content, indent="  "))


async def fetch_all(urls):
    await asyncio.gather(*(fetch(url) for url in urls))


if __name__ == "__main__":
    asyncio.run(fetch_all(urls))

