from bottle import request, route, run

from .sonarqube import SonarQube
from .jenkins import Jenkins
from .junit import JUnit


__title__ = "Quality time"
__version__ = "0.1.0"


@route("/<source>/<url:path>/m/<metric>/<component>")
@route("/<source>/<url:path>/m/<metric>")
def metric(source, *args, **kwargs):
    source = dict(sonarqube=SonarQube, jenkins=Jenkins, junit=JUnit)[source]
    return source.metric(*args, **kwargs)


def quality_time():
    run(server="cherrypy", host='0.0.0.0', port=8080)
