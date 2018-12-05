from bottle import request, route, run

from .sonarqube import SonarQube
from .jenkins import Jenkins
from .junit import JUnit


__title__ = "Quality time"
__version__ = "0.1.0"


@route("/<metric>/<source>")
def get(metric, source):
    urls = request.query.getall("url")
    components = request.query.getall("component")
    source = dict(sonarqube=SonarQube, junit=JUnit)[source]
    return source.get(metric, urls[0], components[0] if components else None)


def quality_time():
    run(server="cherrypy", host='0.0.0.0', port=8080)
