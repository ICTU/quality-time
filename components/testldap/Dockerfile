# update-time: allow[hash-drift]
FROM debian:13.6-slim@sha256:d7e12182ce18b85b93007c1dedf31f2d29e01ccf3182cc4017c709b6259bc132

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
