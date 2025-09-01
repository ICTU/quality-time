#!/bin/sh
set -e

# Get variable or set defaults
declare -rx BOOTSTRAP_DIR=${BOOTSTRAP_DIR:-/bootstrap}
declare -rx LDAP_SECRET=${LDAP_SECRET:-admin}
declare -rx LDAP_DOMAIN=${LDAP_DOMAIN:-example.org}
declare -rx LDAP_ORGANISATION=${LDAP_ORGANISATION:-Example.org}
declare -rx LDAP_DEBUG_LEVEL=${LDAP_DEBUG_LEVEL:-256}

# These are calculated from previous values
declare -rx LDAP_BASEDN="dc=${LDAP_DOMAIN//./,dc=}"
declare -rx LDAP_BINDDN="cn=admin,${LDAP_BASEDN}"

# These are not supposed to be customized for now
declare -rx LDAP_SSL_KEY="/etc/ldap/ssl/ldap.key"
declare -rx LDAP_SSL_CERT="/etc/ldap/ssl/ldap.crt"

if ! [ -f /etc/ldap/slapd-bootstraped ]; then
    echo "Configuring slapd mock instance"
    /bin/bash /slapd-init.sh
    touch /etc/ldap/slapd-bootstraped
fi

echo "starting slapd on port 389 and 636..."
chown -R openldap:openldap /etc/ldap
exec /usr/sbin/slapd -h "ldap:/// ldapi:/// ldaps:///" \
  -u openldap \
  -g openldap \
  -d ${LDAP_DEBUG_LEVEL}
