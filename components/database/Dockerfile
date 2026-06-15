FROM mongo:8.3.2@sha256:94b405c5aa83d5160e6dd97383c4687d471f8a6bd247ed3ff6463c092ebf7a8c

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time database"

# Remove the MongoDB database tools (mongodump, mongorestore, mongoexport, mongostat, etc.). They are not used
# by the server, by Quality-time (the components connect via PyMongo), or for backups (which use a separate
# mongo container, see the deployment documentation), and they ship with their own vulnerabilities. The server
# (mongod) and the shell (mongosh, needed by the entrypoint to create the root user) are kept.
RUN apt-get purge --yes mongodb-database-tools mongodb-org-database-tools-extra && \
    rm -rf /var/lib/apt/lists/*
