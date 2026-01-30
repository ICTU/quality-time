# Versioning policy

This document describes the *Quality-time* versioning policy. It is aimed at *Quality-time* operators and developers.

## Major, minor, and patch releases

*Quality-time* complies with [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

A new **major** release of *Quality-time* is made when operators need to make changes to the Docker-composition (besides upgrading version numbers) before upgrading *Quality-time*.

A new **minor** release of *Quality-time* is made when the new version has new or changed functionality.

A new **patch** release of *Quality-time* is made when the new version has only bug fixes.

## Version overview

The table below contains the *Quality-time* releases since the last minor of the previous major release. For each release it shows:

- Version: the version number of the release.
- Date: the release date.
- Mongo: the {index}`MongoDB` version included.
- FC: the MongoDB feature compatibility (FC) version set in the database.
- Migrations: whether migration code was added or removed in the release.
- Max. downgrade: whether downgrading is supported, and if so, what the lowest version is to which downgrading is supported.
- Max. upgrade: the highest version to which upgrading is supported.
- Manual changes: whether manual changes are needed to up- or downgrade. Manual changes are (by definition) only needed for major releases. The manual changes are documented in the [changelog](changelog.md).

The MongoDB version, the MongoDB feature compatibility, and the migrations all limit the downgrade and upgrade options. See the [background information](#background-information-on-downgrade-and-upgrade-limitations) below.

| Version    | Date       | Mongo  | FC     | Migrations  | Max. downgrade | Max. upgrade | Manual changes |
|------------|------------|--------|--------|-------------|----------------|--------------|----------------|
| v5.48.3    | 2026-01-29 | v8     | v8     |             | v5.47.2        | n/a          | no             |
| v5.48.2    | 2026-01-09 | v8     | v8     |             | v5.47.2        | latest       | no             |
| v5.48.1    | 2025-12-19 | v8     | v8     |             | v5.47.2        | latest       | no             |
| v5.48.0    | 2025-12-12 | v8     | v8     |             | v5.47.2        | latest       | no             |
| v5.47.2    | 2025-12-05 | v8     | v8     | added (3)   | not supported  | latest       | no             |
| v5.47.1    | 2025-11-28 | v8     | v8     | removed (2) | v5.40.0        | latest       | no             |
| v5.47.0    | 2025-11-20 | v8     | v8     |             | v5.40.0        | latest       | no             |
| v5.46.0    | 2025-11-13 | v8     | v8     |             | v5.40.0        | latest       | no             |
| v5.45.0    | 2025-10-31 | v8     | v8     |             | v5.40.0        | latest       | no             |
| v5.44.2    | 2025-10-16 | v8     | v8     |             | v5.40.0        | latest       | no             |
| v5.44.1    | 2025-10-10 | v8     | v8     |             | v5.40.0        | latest       | no             |
| v5.44.0    | 2025-10-03 | v8     | v8     |             | v5.40.0        | latest       | no             |
| v5.43.0    | 2025-09-26 | v8     | v8     |             | v5.40.0        | latest       | no             |
| v5.42.0    | 2025-09-18 | v8     | v8     |             | v5.40.0        | latest       | no             |
| v5.41.0    | 2025-09-05 | v8     | v8     |             | v5.40.0        | latest       | no             |
| v5.40.0    | 2025-08-29 | v8     | v8     | added (1)   | not supported  | latest       | no             |
| v5.39.0    | 2025-08-21 | v8     | v8     |             | v5.38.0        | v5.47.0      | no             |
| v5.38.1    | 2025-08-14 | v8     | v8     |             | v5.38.0        | v5.47.0      | no             |
| v5.38.0    | 2025-08-13 | v8     | v8     | added       | not supported  | v5.47.0      | no             |
| v5.37.0    | 2025-08-06 | v8     | v8     |             | v5.26.0        | v5.47.0      | no             |
| v5.36.0    | 2025-07-10 | v8     | v8     |             | v5.26.0        | v5.47.0      | no             |
| v5.35.0    | 2025-07-04 | v8     | v8     |             | v5.26.0        | v5.47.0      | no             |
| v5.34.0    | 2025-06-26 | v8     | v8     |             | v5.26.0        | v5.47.0      | no             |
| v5.33.0    | 2025-06-20 | v8     | v8     |             | v5.26.0        | v5.47.0      | no             |
| v5.32.1    | 2025-06-12 | v8     | v8     |             | v5.26.0        | v5.47.0      | no             |
| v5.32.0    | 2025-06-05 | v8     | v8     |             | v5.26.0        | v5.47.0      | no             |
| v5.31.0    | 2025-05-22 | v8     | v8     |             | v5.26.0        | v5.47.0      | no             |
| v5.30.0    | 2025-05-15 | v8     | v8     |             | v5.26.0        | v5.47.0      | no             |
| v5.29.0    | 2025-05-08 | v8     | v8     |             | v5.26.0        | v5.47.0      | no             |
| v5.28.0    | 2025-04-17 | v8     | v8     |             | v5.26.0        | v5.47.0      | no             |
| v5.27.0    | 2025-04-04 | v8     | v8     |             | v5.26.0        | v5.47.0      | no             |
| v5.26.2    | 2025-03-20 | v8     | v8     |             | v5.26.0        | v5.47.0      | no             |
| v5.26.1    | 2025-03-19 | v8     | v8     |             | v5.26.0        | v5.47.0      | no             |
| v5.26.0    | 2025-02-27 | v8     | v8     | added       | not supported  | v5.47.0      | no             |
| v5.25.0    | 2025-02-14 | v8     | v8     |             | v5.20.0        | v5.47.0      | no             |
| v5.24.0    | 2025-02-06 | v8     | v8     |             | v5.20.0        | v5.47.0      | no             |
| v5.23.0    | 2025-01-27 | v8     | v8     |             | v5.20.0        | v5.47.0      | no             |
| v5.22.0    | 2025-01-16 | v8     | v8     |             | v5.20.0        | v5.47.0      | no             |
| v5.21.0    | 2024-12-12 | v8     | v8     |             | v5.20.0        | v5.47.0      | no             |
| v5.20.0    | 2024-12-05 | v8     | **v8** | added       | not supported  | v5.47.0      | no             |
| v5.19.0    | 2024-11-22 | v8     | v7     |             | v5.16.1        | v5.47.0      | no             |
| v5.18.0    | 2024-11-06 | v8     | v7     |             | v5.16.1        | v5.47.0      | no             |
| v5.17.1    | 2024-10-25 | v8     | v7     |             | v5.16.1        | v5.47.0      | no             |
| v5.17.0    | 2024-10-17 | **v8** | v7     |             | v5.16.1        | v5.47.0      | no             |
| v5.16.2    | 2024-10-03 | v7     | v7     |             | v5.16.1        | v5.47.0      | no             |
| v5.16.1    | 2024-09-26 | v7     | v7     | added       | not supported  | v5.47.0      | no             |
| v5.16.0    | 2024-09-19 | v7     | v7     | added       | not supported  | v5.47.0      | no             |
| v5.15.0    | 2024-07-30 | v7     | v7     |             | v5.14.0        | v5.47.0      | no             |
| v5.14.0    | 2024-07-05 | v7     | **v7** | added       | not supported  | v5.47.0      | no             |
| v5.13.0    | 2024-05-23 | v7     | v6     | added       | not supported  | v5.16.2      | no             |
| v5.12.0    | 2024-05-17 | v7     | v6     | added       | not supported  | v5.16.2      | no             |
| v5.11.0    | 2024-04-22 | v7     | v6     |             | v5.6.0         | v5.16.2      | no             |
| v5.10.0    | 2024-04-15 | v7     | v6     |             | v5.6.0         | v5.16.2      | no             |
| v5.9.0     | 2024-03-22 | v7     | v6     |             | v5.6.0         | v5.16.2      | no             |
| v5.8.0     | 2024-02-16 | v7     | v6     |             | v5.6.0         | v5.16.2      | no             |
| v5.7.0     | 2024-01-31 | v7     | v6     |             | v5.6.0         | v5.16.2      | no             |
| v5.6.0     | 2024-01-12 | v7     | v6     | added       | not supported  | v5.16.2      | no             |
| v5.5.0     | 2023-12-15 | v7     | v6     |             | v5.1.0         | v5.16.2      | no             |
| v5.4.0     | 2023-12-11 | v7     | v6     |             | v5.1.0         | v5.16.2      | no             |
| v5.3.1     | 2023-11-08 | v7     | v6     |             | v5.1.0         | v5.16.2      | no             |
| v5.3.0     | 2023-11-07 | **v7** | v6     |             | v5.1.0         | v5.16.2      | no             |
| v5.2.0     | 2023-09-29 | v6     | v6     |             | v5.1.0         | v5.16.2      | no             |
| v5.1.0     | 2023-09-05 | v6     | **v6** |             | not supported  | v5.16.2      | no             |
| v5.0.1     | 2023-06-26 | v6     | v5     |             | v4.10.0        | v5.2.0       | no             |
| **v5.0.0** | 2023-06-23 | **v6** | v5     |             | v4.10.0        | v5.2.0       | **yes**        |
| v4.10.0    | 2023-04-26 | v5     | v5     |             | n/a            | v5.2.0       | no             |

(3) [Switch min/max addition strategy when switching metric direction](https://github.com/ICTU/quality-time/issues/12142)

(2) [Removed all current database migrations](https://github.com/ICTU/quality-time/issues/12289):

- Add source parameter hashes to the latest measurements.
- Replace accessibility metrics with violations metrics.
- Set the branch parameter of sources to 'master' (the previous default) if they have no value.
- Remove manual number sources from test cases metrics.
- Change the CI subject type to development environment.
- Replace the SonarQube parameters to adapt to the new (SonarQube 10.2) issue structure.
- Change unmerged branches metrics to inactive branches metrics.
- Change the parameter 'project' of the metric 'inactive branches' to 'project_or_group'.
- Add XML to the OWASP Dependency-Check source key (1).

(1) [Allow for using OWASP Dependency Check JSON as source](https://github.com/ICTU/quality-time/issues/11851).

## Background information on downgrade and upgrade limitations

There are two factors that limit to which versions an existing *Quality-time* instance can be upgraded or downgraded: MongoDB and migration code.

### MongoDB

*Quality-time* uses MongoDB as database. MongoDB sets a feature compatibility version in the database to specify which major version of MongoDB the persisted data is compatible with. When upgrading MongoDB to a new major version, the feature compatibility flag should be set to the previous major version, and only when the upgrade was successful should the feature compatibility flag set to the new major version of MongoDB.

In general, when the feature compatibility of a database is set to version `x`, the database can only be used with MongoDB versions `x` and `x+1`. This limits the down- and upgrade options of *Quality-time* as documented in the table above.

```{seealso}
See the [MongoDB documentation](https://www.mongodb.com/docs/manual/reference/command/setfeaturecompatibilityversion/) on the feature compatibility version.
```

### Migration code

To support changes in the *Quality-time* functionality, data in the database may need to be restructured. To this end, the API-server may run migration code on startup. This migration code is idempotent, meaning that whenever data already has been migrated it does not make any changes. However, migration code is not reversible, meaning that going back a minor or major update is not supported when a release contains new migration code.
