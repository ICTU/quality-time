# Deploying *Quality-time*

(To be completed)

## Frontend

If the frontend is served from a URL starting with `www`, it assumes the server can be reached at the same URL but with `www` replaced by `server` and port 5001. For example, if the frontend is served from `www.quality-time.example.org:5000`, it assumes the server can be reached at `server.quality-time.example.org:5001`.

If the frontend is served from a URL that doesn't start with `www`, it assumes the server can be reached at the same URL, but with port 5001. For example, if the frontend is served from `quality-time.example.org:5000`, it assumes the server can be reached at `quality-time.example.org:5001`. Similarly, if the frontend is served from `localhost:5000`, it assumes the server can be reached at `localhost:5001`.

## LDAP

To configure a LDAP server to authenticate users with, set the `LDAP_URL` and `LDAP_ROOT_DN` environment variables. When running locally, this can be done in the shell:

```console
$ export LDAP_URL="ldap://ldap.example.org:389"
$ export LDAP_ROOT_DN="dc=example,dc=org"
$ quality-report-server
INFO:root:Connected to database: Database(MongoClient(host=['localhost:27017'], document_class=dict, tz_aware=False, connect=True), 'quality_time_db')
INFO:root:Measurements collection has 108 measurements
INFO:root:Initializing LDAP server at ldap://ldap.example.org:389
...
```

When using docker-compose, add the LDAP environment variables to the server section:

```yaml
...
server:
    image: docker-registry.example.org:5000/ictu/quality-time-server
    ports:
    - "5001:5001"
    environment:
    - FRONTEND_URL=http://www.quality-time.example.org:5000
    - SERVER_URL=http://server.quality-time.example.org:5001
    - DATABASE_URL=mongodb://root:root@database:27017
    - LDAP_URL=ldap://ldap.example.org:389
    - LDAP_ROOT_DN="dc=example,dc=org"
```

Users can only use their canonical name (`cn`) to login at the moment.
