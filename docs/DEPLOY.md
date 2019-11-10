# Deploying *Quality-time*

(To be completed)

## Proxy

External traffic is routed by a Caddy reverse proxy (container name: proxy) to either the frontend container or the server container. 

## Frontend

The React UI is served by the frontend container, which runs at port 5000 by default. The Caddy reverse proxy routes external traffic that's not meant for the API to the frontend container. 

## Server

The API is accessible at the server container, running at port 5001 by default. The Caddy reverse proxy routes URLs that start with /api to the server.  

## LDAP

To configure an LDAP server to authenticate users with, set the `LDAP_URL`, `LDAP_ROOT_DN`, `LDAP_LOOKUP_USER_DN`, `LDAP_LOOKUP_USER_PASSWORD`, and `LDAP_SEARCH_FILTER` environment variables. When running locally, this can be done in the shell:

```console
$ export LDAP_URL="ldap://ldap.example.org:389"
$ export LDAP_ROOT_DN="dc=example,dc=org"
$ export LDAP_LOOKUP_USER_DN="cn=lookup_user,dc=example,dc=org"
$ export LDAP_LOOKUP_USER_PASSWORD="secret"
$ export LDAP_SEARCH_FILTER='(|(uid=$username)(cn=$username))'  # Single quotes to prevent the shell from expanding the username variable
$ cd components/server
$ python src/quality_report_server.py
INFO:root:Connected to database: Database(MongoClient(host=['localhost:27017'], document_class=dict, tz_aware=False, connect=True), 'quality_time_db')
INFO:root:Measurements collection has 108 measurements
INFO:root:Initializing LDAP server at ldap://ldap.example.org:389
...
```

When using docker-compose, add the LDAP environment variables to the relevant env file in the docker folder:

```bash
...
# Server
SERVER_PORT=5001
SERVER_HOST=server
DATABASE_URL=mongodb://root:root@database:27017
LDAP_URL=ldap://ldap:389
LDAP_ROOT_DN=dc=example,dc=org
LDAP_LOOKUP_USER_DN=cn=admin,dc=example,dc=org
LDAP_LOOKUP_USER_PASSWORD=admin
LDAP_SEARCH_FILTER=(|(uid=$$username)(cn=$$username))  # Escape the $-sign to prevent docker-compose from expanding the username variable
LOAD_EXAMPLE_REPORTS=True
...
```

When using the `LDAP_SEARCH_FILTER` as shown above, users can use either their LDAP canonical name (`cn`) or their LDAP user id to login. The `$username` variable is filled by *Quality-time* at run time with the username that the user enters in the login dialog box. 

See [https://ldap.com/ldap-filters/](https://ldap.com/ldap-filters/) for more information on LDAP filters.
