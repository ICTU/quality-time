# *Quality-time* test LDAP server

This is a LDAP server included for test purposes. It is based on the `osixia/openldap` Docker image, and adds two extra users. This image is published as `ictu/quality-time_testldap` on Docker Hub.

## LDAP users

The LDAP database has three users: 

| User          | Username | Password |
| ------------- | -------- | -------- |
| Administrator | admin    | admin    |
| Jane Doe      | jadoe    | secret   |
| John Doe      | jodoe    | secret   |

