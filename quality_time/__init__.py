from bottle import request, route, run

from .sources import Jenkins, JUnit, SonarQube


__title__ = "Quality time"
__version__ = "0.1.0"


@route("/<metric>/<source>")
def get(metric, source):
    source = dict(sonarqube=SonarQube, jenkins=Jenkins, junit=JUnit)[source]
    urls = request.query.getall("url")
    components = request.query.getall("component")
    return source.get(metric, urls, components) 


def quality_time():
    run(server="cherrypy", host='0.0.0.0', port=8080, reloader=True)
