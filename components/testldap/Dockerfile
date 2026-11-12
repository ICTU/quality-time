# update-time: allow[hash-drift]
FROM debian:13.7-slim@sha256:f6b08b09a05725f9431502d3b5714f5c4576e82c1a84fa1debe0c24a7e0c3ec4

# Install slapd and requirements
RUN \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    gettext-base \
    ldap-utils \
    openssl \
    slapd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir /etc/ldap/ssl /bootstrap

COPY *.sh /
COPY bootstrap /bootstrap

EXPOSE 389 636

CMD ["/bin/bash", "/run.sh"]
ENTRYPOINT []
