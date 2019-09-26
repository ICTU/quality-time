"""Initialize bottle."""

from pymongo.database import Database
import bottle
from routes.plugins import AuthenticationPlugin, InjectionPlugin
from routes import cors, changelog, report, measurement, datamodel, auth  # pylint: disable=unused-import


def init_bottle(database: Database) -> None:
    """Initialize bottle."""
    bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024  # Max size of POST body in bytes
    bottle.install(InjectionPlugin(value=database, keyword="database"))
    bottle.install(AuthenticationPlugin())
