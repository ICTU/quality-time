from bottle import request, route, run

from .metrics import FailedJobs, Jobs, FailedTests, Tests, NCLOC, Version
from .sources import Jenkins, JUnit, SonarQube
from .type import MeasurementResponse


__title__ = "Quality time"
__version__ = "0.1.0"


@route("/<metric>/<source>")
def get(metric: str, source: str) -> MeasurementResponse:
    metric = dict(failed_jobs=FailedJobs, jobs=Jobs, tests=Tests, failed_tests=FailedTests, ncloc=NCLOC, 
                  version=Version)[metric]
    source = dict(sonarqube=SonarQube, jenkins=Jenkins, junit=JUnit)[source]
    urls = request.query.getall("url")
    components = request.query.getall("component")
    return source.get(metric, urls, components) 


def quality_time():
    run(server="cherrypy", host='0.0.0.0', port=8080, reloader=True)
