FROM debian:13.5-slim@sha256:b6e2a152f22a40ff69d92cb397223c906017e1391a73c952b588e51af8883bf8

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
