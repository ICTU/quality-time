# Deploying *Quality-time*

(To be completed)

## Proxy

External traffic is routed by the Traefik reverse proxy (container name: proxy) to either the frontend container or the server container. 

## Frontend

The React UI is served by the frontend container, which runs at port 5000 by default. The Traefik reverse proxy routes external traffic that's not meant for the API to the frontend container. 

## Server

The API is accessible at the server container, running at port 5001 by default. The Traefik reverse proxy routes URLs that start with /api to the server.  

## LDAP

To configure an LDAP server to authenticate users with, set the `LDAP_URL`, `LDAP_ROOT_DN`, `LDAP_LOOKUP_USER`, and `LDAP_LOOKUP_USER_PASSWORD` environment variables. When running locally, this can be done in the shell:

```console
$ export LDAP_URL="ldap://ldap.example.org:389"
$ export LDAP_ROOT_DN="dc=example,dc=org"
$ export LDAP_LOOKUP_USER=lookup_user
$ export LDAP_LOOKUP_USER_PASSWORD=secret
$ cd components/server
$ python src/quality_report_server.py
INFO:root:Connected to database: Database(MongoClient(host=['localhost:27017'], document_class=dict, tz_aware=False, connect=True), 'quality_time_db')
INFO:root:Measurements collection has 108 measurements
INFO:root:Initializing LDAP server at ldap://ldap.example.org:389
...
```

When using docker-compose, add the LDAP environment variables to the relevant env file in the docker folder:

```yaml
...
# Server
SERVER_PORT=5001
DATABASE_URL=mongodb://root:root@database:27017
LDAP_URL=ldap://ldap.example.org:389
LDAP_LOOKUP_USER=lookup
LDAP_LOOKUP_USER_PASSWORD=secret
...
```

Users can use either their LDAP canonical name (`cn`) or their LDAP user id to login.
