import logging
from typing import Dict, NewType, Optional, Tuple, Union
import xml.etree.cElementTree

from bottle import request, route, run
import requests


URL = NewType("URL", str)
Measurement = str
ErrorMessage = str
MeasurementResponse = Dict[str, Union[Optional[str], Optional[URL], Optional[Measurement], Optional[ErrorMessage]]]

class Source:
    TIMEOUT = 10  # Default timeout of 10 seconds

    @classmethod
    def metric(cls, url: URL, metric: str, component: str = None) -> MeasurementResponse:
        """Connect to the the source to get and parse the measurement for the metric."""
        landing_url = cls.landing_url(url, metric, component or "")
        api_url = cls.api_url(url, metric, component or "")
        response, connection_error = cls.safely_get_source_response(api_url)
        measurement, parse_error = cls.safely_parse_source_response(metric, response) if response else (None, None)
        return dict(source=cls.__name__, metric=metric, component=component, url=url, api_url=api_url, landing_url=landing_url, 
                    connection_error=connection_error, parse_error=parse_error, measurement=measurement)

    @classmethod
    def landing_url(cls, url: URL, metric: str, component: str) -> Optional[URL]: 
        """Translate the url into the landing url.""" 
        return None

    @classmethod
    def api_url(cls, url: URL, metric: str, component: str) -> URL: 
        """Translate the url into the API url.""" 
        return url

    @classmethod
    def safely_get_source_response(cls, url: URL) -> Tuple[Optional[requests.Response], Optional[ErrorMessage]]:
        """Connect to the source and get the data, without failing.""" 
        response, error = None, None
        try:
            response = cls.get_source_response(url)
        except Exception as reason:
            error = ErrorMessage(reason)
        return response, error

    @classmethod 
    def get_source_response(cls, url: URL) -> requests.Response:
        """Open the url. Raise an exception if the response status isn't 200 or if a time out occurs."""
        response = requests.get(url, timeout=cls.TIMEOUT)
        response.raise_for_status()
        return response

    @classmethod
    def safely_parse_source_response(cls, metric: str, response: requests.Response) -> Tuple[Optional[Measurement], Optional[ErrorMessage]]:
        """Parse to the measurement from the response, without failing.""" 
        measurement, error = None, None
        try:
            measurement = cls.parse_source_response(metric, response) 
        except Exception as reason:
            error = ErrorMessage(reason)
        return measurement, error

    @classmethod 
    def parse_source_response(cls, metric: str, response: requests.Response) -> Measurement:
        """Parse the response to get the measurement for the metric."""
        raise NotImplementedError


class SonarQube(Source):
    @classmethod
    def landing_url(cls, url: URL, metric: str, component: str) -> Optional[URL]:
        if metric == "issues":
            return URL(f"{url}/project/issues?id={component}&resolved=false")
        elif metric != "version":
            return URL(f"{url}/component_measures?id={component}&metric={metric}")
        return url

    @classmethod
    def api_url(cls, url: URL, metric: str, component: str) -> URL:
        apis = dict(version="server/version", issues=f"issues/search?componentKeys={component}&resolved=false")
        api = apis.get(metric, f"measures/component?component={component}&metricKeys={metric}")
        return URL(f"{url}/api/{api}")

    @classmethod 
    def parse_source_response(cls, metric: str, response: requests.Response) -> Measurement:
        if metric == "version":
            return response.text
        json = response.json()
        if metric == "issues":
            return json["total"]
        return Measurement(json["component"]["measures"][0]["value"])
        

class Jenkins(Source):
    @classmethod
    def api_url(cls, url: URL, metric: str, component: str) -> URL:
        return URL(f"{url}/api/json?tree=jobs[buildable,color]")

    @classmethod
    def parse_source_response(cls, metric: str, response: requests.Response) -> Measurement:
        jobs = [job for job in response.json()["jobs"] if job.get("buildable", False)]
        if metric == "failing_jobs":
            jobs = [job for job in jobs if not job.get("color", "").startswith("blue")]
        return Measurement(len(jobs))


class JUnit(Source):
    @classmethod
    def parse_source_response(cls, metric: str, response: requests.Response) -> Measurement:
        test_suites = xml.etree.cElementTree.fromstring(response.text).findall("testsuite")
        return Measurement(sum(int(test_suite.get(metric, 0)) for test_suite in test_suites))


@route("/<source>/<url:path>/m/<metric>/<component>")
@route("/<source>/<url:path>/m/<metric>")
def metric(source, *args, **kwargs):
    source = dict(sonarqube=SonarQube, jenkins=Jenkins, junit=JUnit)[source]
    return source.metric(*args, **kwargs)


run(server="cherrypy", host='0.0.0.0', port=8080)

