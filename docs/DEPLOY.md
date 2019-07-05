# Deploying *Quality-time*

(To be completed)

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
