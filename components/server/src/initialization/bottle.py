"""Initialize bottle."""

from pymongo.database import Database
import bottle
from routes.plugins import AuthenticationPlugin, InjectionPlugin
# pylint: disable=unused-import
from routes import (
    auth, changelog, datamodel, documentation, measurement, metric, report, reports, source, subject)


def init_bottle(database: Database) -> None:
    """Initialize bottle."""
    bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024  # Max size of POST body in bytes
    bottle.install(InjectionPlugin(value=database, keyword="database"))
    bottle.install(AuthenticationPlugin())
