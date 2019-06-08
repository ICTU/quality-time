"""Quality-time server."""

from gevent import monkey
monkey.patch_all()

# pylint: disable=wrong-import-order,wrong-import-position

import logging
import os

import bottle
import ldap
import pymongo

from . import cors  # pylint: disable=unused-import
from .initialization.datamodel import import_datamodel
from .initialization.report import import_example_reports
from .routes import report, measurement, datamodel, auth  # pylint: disable=unused-import
from .route_injection_plugin import InjectionPlugin
from .route_authentication_plugin import AuthenticationPlugin


def serve() -> None:
    """Connect to the database and start the application server."""
    logging.getLogger().setLevel(logging.INFO)
    bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024  # Max size of POST body in bytes
    database_url = os.environ.get("DATABASE_URL", "mongodb://root:root@localhost:27017")
    database = pymongo.MongoClient(database_url).quality_time_db
    logging.info("Connected to database: %s", database)
    logging.info("Measurements collection has %d measurements", database.measurements.count_documents({}))
    ldap_url = os.environ.get("LDAP_URL", "ldap://localhost:389")
    logging.info("Initializing LDAP server at %s", ldap_url)
    ldap_server = ldap.initialize(ldap_url)
    ldap_injection_plugin = InjectionPlugin(value=ldap_server, keyword="ldap_server")
    bottle.install(ldap_injection_plugin)
    database_injection_plugin = InjectionPlugin(value=database, keyword="database")
    bottle.install(database_injection_plugin)
    bottle.install(AuthenticationPlugin())
    import_datamodel(database)
    import_example_reports(database)
    bottle.run(server="gevent", host='0.0.0.0', port=8080, reloader=True)
