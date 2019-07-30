# Releasing *Quality-time*

To release *Quality-time*, follow these steps (in the project root folder):

```console
python3 -m venv venv
. venv/bin/activate
pip install -r requirements-dev.txt
ci/release.py major|minor|patch
```

The `release.py` script will bump the version numbers, update the change history, commit the changes, push the commit, tag the commit, and push the tag to Github. The [Travis CI](https://travis-ci.org/ICTU/quality-time) pipeline will then run the tests and, if the tests are successful, build the Docker containers and push them to [Docker Hub](https://cloud.docker.com/u/ictu/repository/list?name=quality-time&namespace=ictu).

The Docker containers are `quality-time_collector`, `quality-time_receiver`, `quality-time_server`, and `quality-time_frontend`. We don't use the `latest` tag.
