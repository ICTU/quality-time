"""Initialize bottle."""

import bottle
from pymongo.database import Database

from routes import *  # noqa: F403
from routes.plugins import AuthPlugin, InjectionPlugin


def init_bottle(database: Database) -> None:
    """Initialize bottle."""
    bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024  # Max size of POST body in bytes
    bottle.install(InjectionPlugin(value=database, keyword="database"))
    bottle.install(AuthPlugin())
