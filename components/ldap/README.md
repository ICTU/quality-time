# *Quality-time* test LDAP server

This is an LDAP server included for test purposes. It is based on the `osixia/openldap` Docker image, and adds two extra users. This image is published as `ictu/quality-time_testldap` on Docker Hub.

## LDAP users

The LDAP database has two (*) users:

| User          | Email address       | Username | Password |
| ------------- | ------------------- | -------- | -------- |
| Jane Doe      | janedoe@example.org | jadoe    | secret   |
| John Doe      | johndoe@example.org | jodoe    | secret   |

(*) The `osixia/openldap` Docker image normally has an administrator user as well, but due to [this issue in OpenLDAP 1.5.0](https://github.com/osixia/docker-openldap/issues/555) this user is currently not available. 
