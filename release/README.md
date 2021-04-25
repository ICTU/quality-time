# Releasing *Quality-time*

## Preparation

Make sure the release folder is the current directory, and you have the dependencies for the release script installed:

```console
cd release
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

Run the release script with `--help` to show help information.

```console
python release.py --help
```

## Pick the release type 

*Quality-time* adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html), so first you need to determine the release type:

- Create a **major** release if the next release contains backwards incompatible changes, and optionally other changes and bug fixes.
- Create a **minor** release if the next release contains non-breaking changes, and optionally bug fixes.
- Create a **patch** release if the next release contains bug fixes only.

If you want to test the release (for example, deploy it to a test environment, or roll out a release to early adopters), it's possible to create a **release candidate** for a major, minor, or patch release.

Note: to determine whether a release is major, minor, or patch, compare the changes to the previous most recent release, excluding release candidates.

## Determine the version bump

This leads to the following possibilities for the version bump argument that you will be passing to the release script:

- If the current release is a release candidate,
  - and you want to create another release candidate, use: `rc`. If the current release is e.g. v3.6.1-rc.0, this will bump the version to v3.6.1-rc.1.
  - and the next release will not be, use: `drop-rc`. If the current release is e.g. v3.6.1-rc.0, this will bump the version to v3.6.1.
- If the current release is not a release candidate:
  - and you want to create a release candidate, use: `rc-major`, `rc-minor`, or `rc-patch`. If the current release is e.g. v3.6.1, using `rc-minor` will bump the version to v3.7.0-rc.0.
  - and you don't want to create a release candidate, use: `major`, `minor`, or `patch`. If the current release is e.g. v3.6.1, using `minor` will bump the version to v3.7.0.

## Check the preconditions

The release script will check a number of preconditions before actually creating the release. To check the preconditions
without releasing, invoke the release script with the version bump as determined:

```console
python release.py --check-preconditions-only <bump>  # Where bump is major, minor, patch, rc-major, rc-minor, rc-patch, rc, or drop-rc
```

If everything is ok, there is no output, and you can proceed creating the release. Otherwise, the release script will list the preconditions that have not been met and need fixing before you can create the release. 

## Create the release

To release *Quality-time*, issue the release command (in the release folder) using the type of release you picked:

```console
python release.py <bump>  # Where bump is major, minor, patch, rc-major, rc-minor, rc-patch, rc, or drop-rc
```

If all preconditions are met, the release script will bump the version numbers, update the change history, commit the changes, push the commit, tag the commit, and push the tag to GitHub. The [GitHub Actions release workflow](https://github.com/ICTU/quality-time/actions/workflows/release.yml) will then build the Docker images and push them to [Docker Hub](https://cloud.docker.com/u/ictu/repository/list?name=quality-time&namespace=ictu).

The Docker images are `quality-time_database`, `quality-time_renderer`, `quality-time_server`, `quality-time_collector`, `quality-time_notifier`, `quality-time_proxy`, `quality-time_testldap`, and `quality-time_frontend`. The images are tagged with the version number. We don't use the `latest` tag.
