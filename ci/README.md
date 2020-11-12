# Releasing *Quality-time*

## Preparation

Make sure you have the dependencies for the release script installed:

```console
python3 -m venv venv
. venv/bin/activate
pip install -r requirements-dev.txt
```

## Pick the release type

Check the [current most recent release](https://github.com/ICTU/quality-time/releases). There are two scenario's:

1. the current most recent release is a major (e.g. v2.0.0), minor (e.g. v2.3.0), or patch (e.g. v2.3.2) release, or
2. the current most recent release is a release candidate (e.g. v2.4.0-rc.2).

In the first scenario, you have the following options:

- If the next release only contains bug fixes, you'll be creating a `patch` release. If you want to create a release candidate first, you'll be creating a `rc-patch` release.
- If the next release contains non-breaking changes (and optionally bug fixes), you'll be creating a `minor` release. If you want to create a release candidate first, you'll be creating a `rc-minor` release.
- If the next release contains backwards incompatible changes (and optionally other changes and bug fixes), you'll be creating a `major` release. If you want to create a release candidate first, you'll be creating a `rc-major` release.

In the second scenario, you have two options:

- You can create another release candidate (`rc`).
- You can create the major, minor, or patch release that you have been releasing the candidate(s) for (`drop-rc`).

## Check the preconditions

The release script will check a number of preconditions before actually creating the release. To check the preconditions without releasing, invoke the release script as follows:

```console
python ci/release.py --check-preconditions-only major|minor|patch|rc-major|rc-minor|rc-patch|rc|drop-rc
```

## Create the release

To release *Quality-time*, issue the release command (in the project root folder) using the type of release you picked:

```console
python ci/release.py major|minor|patch|rc-major|rc-minor|rc-patch|rc|drop-rc
```

The `release.py` script will bump the version numbers, update the change history, commit the changes, push the commit, tag the commit, and push the tag to Github. The GitHub release workflow will then build the Docker containers and push them to [Docker Hub](https://cloud.docker.com/u/ictu/repository/list?name=quality-time&namespace=ictu).

The Docker containers are `quality-time_server`, `quality-time_collector`, `quality-time_notifier`, and `quality-time_frontend`. We don't use the `latest` tag.
