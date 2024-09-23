# Versioning policy

This document describes the *Quality-time* versioning policy. It is aimed at *Quality-time* operators and developers.

## Major, minor, and patch releases

*Quality-time* complies with [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

A new **major** release of *Quality-time* is made when operators need to make changes to the Docker-composition (besides upgrading version numbers) before upgrading *Quality-time*.

A new **minor** release of *Quality-time* is made when the new version has new or changed functionality.

A new **patch** release of *Quality-time* is made when the new version has only bug fixes.

```{index} MongoDB
```

## Version overview

The table below contains the *Quality-time* releases since the last minor of the previous major release. For each release it shows the release date, the MongoDB version included, the MongoDB feature compatibility (FC) version set in the database, whether migration code was added or removed, and whether up- or downgrading is possible, and if so, to which versions.

| Version    | Date         | Mongo  | FC     | Migrations | Downgrade       | Upgrade         |
|------------|--------------|--------|--------|------------|-----------------|-----------------|
| v5.16.1    | [unreleased] | v7     | v7     |            | v5.14.0-v5.16.0 | n/a             |
| v5.16.0    | 2024-09-19   | v7     | v7     | added      | v5.14.0-v5.15.0 | v5.16.1         |
| v5.15.0    | 2024-07-30   | v7     | v7     |            | v5.14.0         | v5.16.0-v5.16.1 |
| v5.14.0    | 2024-07-05   | v7     | **v7** | added      | not possible    | v5.15.0-v5.16.1 |
| v5.13.0    | 2024-05-23   | v7     | v6     | added      | not possible    | v5.14.0-v5.16.1 |
| v5.12.0    | 2024-05-17   | v7     | v6     | added      | not possible    | v5.13.0-v5.16.1 |
| v5.11.0    | 2024-04-22   | v7     | v6     |            | v5.6.0-v5.10.0  | v5.12.0-v5.16.1 |
| v5.10.0    | 2024-04-15   | v7     | v6     |            | v5.6.0-v5.9.0   | v5.11.0-v5.16.1 |
| v5.9.0     | 2024-03-22   | v7     | v6     |            | v5.6.0-v5.8.0   | v5.10.0-v5.16.1 |
| v5.8.0     | 2024-02-16   | v7     | v6     |            | v5.6.0-v5.7.0   | v5.9.0-v5.16.1  |
| v5.7.0     | 2024-01-31   | v7     | v6     |            | v5.6.0          | v5.8.0-v5.16.1  |
| v5.6.0     | 2024-01-12   | v7     | v6     | added      | not possible    | v5.7.0-v5.16.1  |
| v5.5.0     | 2023-12-15   | v7     | v6     |            | v5.1.0-v5.4.0   | v5.6.0-v5.16.1  |
| v5.4.0     | 2023-12-11   | v7     | v6     |            | v5.1.0-v5.3.1   | v5.5.0-v5.16.1  |
| v5.3.1     | 2023-11-08   | v7     | v6     |            | v5.1.0-v5.3.0   | v5.4.0-v5.16.1  |
| v5.3.0     | 2023-11-07   | **v7** | v6     |            | v5.1.0-v5.2.0   | v5.3.1-v5.16.1  |
| v5.2.0     | 2023-09-29   | v6     | v6     |            | v5.1.0          | v5.3.0-v5.16.1  |
| v5.1.0     | 2023-09-05   | v6     | **v6** |            | not possible    | v5.2.0-v5.16.1  |
| v5.0.1     | 2023-06-26   | v6     | v5     |            | v4.10.0-v5.0.0  | v5.1.0-v5.2.0   |
| **v5.0.0** | 2023-06-23   | **v6** | v5     |            | v4.10.0         | v5.0.1-v5.2.0   |
| v4.10.0    | 2023-04-26   | v5     | v5     |            | n/a             | v5.0.0-v5.2.0   |

## Upgrade path

To check whether versions can be skipped when upgrading *Quality-time*, look up the currently deployed *Quality-time* version in the table above. The "Upgrade" column shows which newer versions of *Quality-time* can be deployed.

For example, if the currently deployed version is v5.0.0, the "Upgrade" column shows that all versions from v5.0.1 up to and including v5.2.0 can be deployed.

```{warning}
When upgrading across a major version, the manual changes as documented in the [changelog](changelog.md) need to be applied.
```

## Downgrade path

To check whether a version of *Quality-time* can be downgraded, look up the currently deployed *Quality-time* version in the table above. The "Downgrade" column shows which older versions of *Quality-time* can be deployed.

For example, if the currently deployed version is v5.5.0, the "Downgrade" column shows that all versions from v5.1.0 up to and including v5.4.0 can be deployed.

```{warning}
When downgrading across a major version, the manual changes as documented in the [changelog](changelog.md) need to be undone.
```

## Background information on down- and upgrade limitations

There are two factors that limit to which versions an existing *Quality-time* instance can be upgraded or downgraded: MongoDB and migration code.

### MongoDB

*Quality-time* uses MongoDB as database. MongoDB sets a feature compatibility version in the database to specify which major version of MongoDB the persisted data is compatible with. When upgrading MongoDB to a new major version, the feature compatibility flag should be set to the previous major version, and only when the upgrade was successful should the feature compatibility flag set to the new major version of MongoDB.

In general, when the feature compatibility of a database is set to version `x`, the database can only be used with MongoDB versions `x` and `x+1`. This limits the down- and upgrade options of *Quality-time* as documented in the table above.

```{seealso}
See the [MongoDB documentation](https://www.mongodb.com/docs/manual/reference/command/setFeatureCompatibilityVersion/) on the feature compatibility version.
```

### Migration code

To support changes in the *Quality-time* functionality, data in the database may need to be restructured. To this end, the API-server may run migration code on startup. This migration code is idempotent, meaning that whenever data already has been migrated it does not make any changes. However, migration code is not reversible, meaning that going back a minor or major update is not possible when a release contains new migration code.
