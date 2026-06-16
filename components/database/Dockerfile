FROM mongo:8.3.3@sha256:9c1d999aad9357e865f000c8cd4937bf2698ff943b9b584a2f3d7860ebfef142

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time database"

# Remove the MongoDB database tools (mongodump, mongorestore, mongoexport, mongostat, etc.). They are not used
# by the server, by Quality-time (the components connect via PyMongo), or for backups (which use a separate
# mongo container, see the deployment documentation), and they ship with their own vulnerabilities. The server
# (mongod) and the shell (mongosh, needed by the entrypoint to create the root user) are kept.
# Make the data directories group-owned by the root group (GID 0) and group-writable so the container can run
# as an arbitrary non-root user (some platforms, such as OpenShift, assign a random high UID with GID 0). This,
# combined with running as non-root, means gosu is no longer needed and can be removed to reduce the attack surface.
RUN apt-get purge --yes mongodb-database-tools mongodb-org-database-tools-extra && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /usr/local/bin/gosu && \
    chgrp -R 0 /data/db /data/configdb && \
    chmod -R g=u /data/db /data/configdb

# Run as the non-root MongoDB user by default. Platforms that require a UID >= 1000 can override this with a
# securityContext (see the deployment documentation); the data directories above are group-writable for GID 0.
USER 999
