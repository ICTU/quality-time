"""Initialize bottle."""

import bottle
from pymongo.database import Database

from routes.plugins import AuthenticationPlugin, InjectionPlugin

# isort: off
# pylint: disable=unused-import
from routes import (  # lgtm [py/unused-import]
    auth, changelog, datamodel, documentation, measurement, metric, report, reports, source, subject)
# isort: on


def init_bottle(database: Database) -> None:
    """Initialize bottle."""
    bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024  # Max size of POST body in bytes
    bottle.install(InjectionPlugin(value=database, keyword="database"))
    bottle.install(AuthenticationPlugin())
