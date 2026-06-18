FROM mongo:8.3.3@sha256:9c1d999aad9357e865f000c8cd4937bf2698ff943b9b584a2f3d7860ebfef142

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time database"

# Remove the MongoDB database tools (mongodump, mongorestore, mongoexport, mongostat, etc.). They are not used
# by the server, by Quality-time (the components connect via PyMongo), or for backups (which use a separate
# mongo container, see the deployment documentation), and they ship with their own vulnerabilities. The server
# (mongod) and the shell (mongosh, needed by the entrypoint to create the root user) are kept.
RUN apt-get purge --yes mongodb-database-tools mongodb-org-database-tools-extra && \
    rm -rf /var/lib/apt/lists/*
