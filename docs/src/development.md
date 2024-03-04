# Developer manual

This document is aimed at *Quality-time* developers and maintainers and describes how to develop, test, document, release, and maintain *Quality-time*. To read more about how *Quality-time* is structured, see the [software documentation](software.md).

## Developing

### Running *Quality-time* locally

When developing *Quality-time*, there are two ways to run *Quality-time* locally: in Docker completely (scenario 1 below) or partly in Docker and partly from shells (scenario 2 below).

If you want to get *Quality-time* up and running quickly, for example for a demo, we recommend scenario 1. For software development, we recommend scenario 2.

#### Install prerequisites

Prerequisites are Docker and Git for both scenario's. For scenario 2 you also need Python 3.12 and a recent version of Node.js (we currently use Node.js v20).

Clone this repository:

```console
git clone git@github.com:ICTU/quality-time.git
cd quality-time
```

If you don't have a public key in your GitHub account, use:

```console
git clone https://github.com/ICTU/quality-time.git
cd quality-time
```

#### Scenario 1: run all components in Docker

To run *Quality-time* in Docker completely, open a terminal and start all containers with docker compose:

```console
docker compose up
```

The advantage of this scenario is that Python and Node.js don't need to be installed. However, as building the containers can be time-consuming we don't recommend this for working on the Quality-time source code.

#### Scenario 2: run bespoke component from shells and other components in Docker

In this scenario, we run the [bespoke components](software.md#bespoke-components) from shells and the [standard components](software.md#standard-components) and [test components](software.md#test-components) as Docker containers.

The advantage of this scenario is that you don't need to rebuild the bespoke container images while developing. Also, the server component and the frontend component have auto-reload, meaning that when you edit the code, they will restart and run the new code automatically. The collector and notifier components don't have auto-reload, and need to stopped and started by hand to activate new code.

##### Start standard and test components in Docker

Open a terminal and start the [standard containers](software.md#standard-components) and [test components](software.md#test-components) with docker compose:

```console
docker compose up database ldap phpldapadmin mongo-express testdata
```

{index}`PHP-LDAP-admin` is served at [http://localhost:3890](http://localhost:3890) and can be used to inspect and edit the {index}`LDAP` database. Click login, check the "Anonymous" box and click "Authenticate" to login.

{index}`Mongo-express` is served at [http://localhost:8081](http://localhost:8081) and can be used to inspect and edit the database contents.

The test data is served at [http://localhost:8080](http://localhost:8080).

There are two users defined in the LDAP database:

- User `Jane Doe` has user id `jadoe` and password `secret`.
- User `John Doe` has user id `jodoe` and password `secret`.

##### Start the {index}`API-server <API-server component>`

Open another terminal and run the API-server:

```console
cd components/api_server
python3 -m venv venv
. venv/bin/activate  # on Windows: venv\Scripts\activate
ci/pip-install.sh
python src/quality_time_server.py
```

The API of the API-server is served at [http://localhost:5001](http://localhost:5001), e.g. access [http://localhost:5001/api/internal/report](http://localhost:5001/api/internal/report) to get the available reports combined with their recent measurements.

```{note}
If you're new to Python virtual environments, note that:
- Creating a virtual environment (`python3 -m venv venv`) has to be done once. Only when the Python version changes, you want to recreate the virtual environment.
- Activating the virtual environment (`. venv/bin/activate`) has to be done every time you open a new shell and want to use the Python installed in the virtual environment.
- Installing the requirements (`ci/pip-install.sh`) has to be repeated when the dependencies, specified in the requirements files, change.
```

```{seealso}
- See the [Python docs](https://docs.python.org/3/library/venv.html) for more information on creating virtual environments.
- See this [Gist](https://gist.github.com/fniessink/f4142927d20fe845dc27a8ad21f340d5) on how to automatically activate and deactivate Python virtual environments when changing directories.
```

##### Start the {index}`collector <Collector component>`

Open another terminal and run the collector:

```console
cd components/collector
python3 -m venv venv
. venv/bin/activate  # on Windows: venv\Scripts\activate
ci/pip-install.sh
python src/quality_time_collector.py
```

##### Start the {index}`frontend <Frontend component>`

Open another terminal and run the frontend:

```console
cd components/frontend
npm install --ignore-scripts
npm run start
```

The frontend is served at [http://localhost:3000](http://localhost:3000).

##### Start the {index}`notifier <Notifier component>`

Optionally, open yet another terminal and run the notifier:

```console
cd components/notifier
python3 -m venv venv
. venv/bin/activate  # on Windows: venv\Scripts\activate
ci/pip-install.sh
python src/quality_time_notifier.py
```

#### Preparing the shared component

*Quality-time* has one component that only contains shared code. The shared code is used by all Python components.

To create a virtual environment for the shared component and install the dependencies run the following:

```console
cd components/shared_code
python3 -m venv venv
. venv/bin/activate  # on Windows: venv\Scripts\activate
ci/pip-install.sh
```

### Coding style

This section contains some notes on coding style used in this project. It's far from complete, however.

#### {index}`Python <pair: Coding style;Python>`

Most of the coding standard are enforced by the [quality checks](#quality-checks).

Methods that can or should be overridden in subclasses have a name with one leading underscore, e.g. `_api_url(self) -> URL`. Methods that should only be used by a class instance itself have a name with two leading underscores, e.g. `__fields(self) -> List[str]`.

Production code and unit tests are organized in parallel hierarchies. Each Python component has a `src` with the production code and a `tests` folder with the unit tests. The folder layout of the `tests` follows the layout of the `src` hierarchy.

#### {index}`JavaScript <pair: Coding style;JavaScript>`

Functional React components are preferred over class-based components.

Production code and unit tests are organized together in one `src` folder hierarchy.

### Adding metrics and sources

*Quality-time* has been designed with the goal of making it easy to add new metrics and sources. The [data model](software.md#data-model) specifies all the details about metrics and sources, like the scale and unit of metrics, and the parameters needed for sources. In general, to add a new metric or source, only the data model and the [collector](software.md#collector) need to be changed.

#### Adding a new metric

To add a new metric you need to make two changes to the data model:

1. Add a specification of the new metric to the data model. See the documentation of the [shared data model](software.md#shared-data-model) component for a description of the data model and the different metric fields.
2. Update the `metric_type` parameter of the `quality_time` source in the data model. You need to add the human readable name of the new metric to the `values` list of the `metric_type` parameter and you need to add a key-value pair to the `api_values` mapping of the `metric_type` parameter, where the key is the human readable name of the metric and the value is the metric key.

Be sure to run the unit tests of the shared data model component after adding a metric to the data model, to check the integrity of the data model. If you forget to do step 2 above, one of the tests will fail. Other than changing the data model, no code changes are needed to support new metrics.

Suppose we want to add a lines of code metric to the data model, to measure the size of software. We would add the metric to the `METRICS` model in `src/shared_data_model/metrics.py`:

```python
"""Data model metrics."""

from .meta.metric import ..., Metric, Tag, Unit

...

METRICS = {
    ...
    "loc": Metric(
        name="Size (LOC)",
        description="The size of the software in lines of code.",
        rationale="The size of software is correlated with the effort it takes to maintain it. Lines of code is "
        "one of the most widely used metrics to measure size of software.",
        unit=Unit.LINES,
        target="30000",
        near_target="35000",
        sources=["manual_number"],
        tags=[Tag.MAINTAINABILITY],
    ),
    ...
}
```

Since we have no (automated) source for the size metric yet, we have added manual number to the list of sources. We also need to add the size metric to the list of metrics that the manual number source supports:

```python
"""Manual number source."""

from ..meta.source import Source
...
from ..parameters import IntegerParameter


MANUAL_NUMBER = Source(
    name="Manual number",
    description="A number entered manually by a Quality-time user.",
    parameters=dict(
        number=IntegerParameter(
            ...
            metrics=[
                ...
                "loc",  # Add the size metric here
                ...
            ],
        )
    ),
)
```

After restart of the API-server, you should be able to add the new metric to a quality report and select manual number as a source for the new metric.

#### Adding a new source

To add support for a new source, the source (including a logo) needs to be added to the data model. In addition, code to retrieve and parse the source data needs to be added to the collector component, including unit tests of course.

##### Adding a new source to the data model

To add a new source you need to make three changes to the data model:

1. Add a specification of the source to the data model. See the documentation of the [shared data model](software.md#shared-data-model) component for a description of the data model and the different source fields.
2. Update the `source_type` parameter of the `quality_time` source in the data model. You need to add the human readable name of the new source to the `values` list of the `source_type` parameter and you need to add a key-value pair to the `api_values` mapping of the `source_type` parameter, where the key is the human readable name of the source and the value is the metric source key (`cloc` in the example below).
3. Add a small PNG file of the logo in [`components/shared_code/src/shared_data_model/logos`](https://github.com/ICTU/quality-time/tree/master/components/shared_code/src/shared_data_model/logos). Make sure the filename of the logo is `<source_type>.png`. The frontend will use the `api/internal/logo/<source_type>` endpoint to retrieve the logo.

Be sure to run the unit tests of the shared data model component after adding a source to the data model, to check the integrity of the data model. If you forget to do step 2 above, one of the tests will fail.

Suppose we want to add [cloc](https://github.com/AlDanial/cloc) as source for the LOC (size) metric and read the size of source code from the JSON file that cloc can produce. We would add a `cloc.py` to `src/shared_data_model/sources/`:

```python
"""cloc source."""

from ..meta.source import Source
from ..parameters import access_parameters


CLOC = Source(
    name="cloc",
    description="cloc is an open-source tool for counting blank lines, comment lines, and physical lines of source "
    "code in many programming languages.",
    url="https://github.com/AlDanial/cloc",
    parameters=dict(
        **access_parameters(["loc"], source_type="cloc report", source_type_format="JSON")
    ),
)
```

Because cloc can be used to measure the lines of code metric, we need to add the cloc source to the list of sources that can measure lines of code:

```python
METRICS = {
    ...
    "loc": Metric(
        name="Size (LOC)",
        description="The size of the software in lines of code.",
        rationale="The size of software is correlated with the effort it takes to maintain it. Lines of code is "
        "one of the most widely used metrics to measure size of software.",
        unit=Unit.LINES,
        target="30000",
        near_target="35000",
        sources=["cloc", "manual_number"],  # Add cloc here
        tags=[Tag.MAINTAINABILITY],
    ),
    ...
}
```

##### Adding a new source to the collector

To specify how *Quality-time* can collect data from the source, a new subclass of [`SourceCollector`](https://github.com/ICTU/quality-time/blob/master/components/collector/src/base_collectors/source_collector.py) needs to be created.

Add a new Python package to the [`source_collectors` folder](https://github.com/ICTU/quality-time/tree/master/components/collector/src/source_collectors) with the same name as the source type in the data model. For example, if the new source type is `cloc`, the folder name of the collectors is also `cloc`. Next, create a module for each metric that the new source supports. For example, if the new source `cloc` supports the metric LOC (size) and the metric source-up-to-dateness, you would create two modules, each containing a subclass of `SourceCollector`: a `ClocLOC` class in `cloc/loc.py` and a `ClocSourceUpToDateness` class if `cloc/source_up_to_dateness.py`. If code can be shared between these classes, add a `cloc/base.py` file with a `ClocBaseClass`.

To reduce duplication, `SourceCollector` has several abstract subclasses. The class hierarchy is currently as follows:

- `SourceCollector`
  - `UnmergedBranchesSourceCollector`: for sources that collect data for the number of unmerged branches metric
  - `TimeCollector`: for sources that collect time since or until a certain moment in time
    - `TimePassedCollector`: for source-up-to-dateness
      - `JenkinsPluginSourceUpToDatenessCollector`: for getting the source-up-to-dateness from Jenkins plugins
    - `TimeRemainingCollector`: for sources that time remaining until a future date
  - `SourceVersionCollector`: for sources that report version numbers
  - `SlowTransactionsCollector`: for sources that report slow performance transactions
  - `JenkinsPluginCollector`: for sources that collect their data from Jenkins plugins
  - `FileSourceCollector`: for sources that parse files
    - `CSVFileSourceCollector`: for sources that parse CSV files
    - `HTMLFileSourceCollector`: for sources that parse HTML files
    - `JSONFileSourceCollector`: for sources that parse JSON files
    - `XMLFileSourceCollector`: for sources that parse XML files

To support [cloc](https://github.com/AlDanial/cloc) as source for the LOC (size) metric we need to read the size of source code from the JSON file that cloc can produce. We add a `cloc/loc.py` file and in `loc.py` we create a `ClocLOC` class with `JSONFileSourceCollector` as super class. The only method that needs to be implemented is `_parse_source_responses()` to get the amount of lines from the cloc JSON file. This could be as simple as:

```python
"""cloc lines of code collector."""

from base_collectors import JSONFileSourceCollector
from model import SourceMeasurement, SourceResponses


class ClocLOC(JSONFileSourceCollector):
    """cloc collector for size/lines of code."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        loc = 0
        for response in responses:
            for key, value in (await response.json()).items():
                if key not in ("header", "SUM"):
                    loc += value["code"]
        return SourceMeasurement(value=str(loc))
```

Most collector classes are a bit more complex than that, because to retrieve the data they have to deal with APIs and while parsing the data they have to take parameters into account. See the collector source code for more examples.

###### Writing and running unit tests

To test the `ClocLOC` collector class, we add unit tests to the [collector tests package](https://github.com/ICTU/quality-time/tree/master/components/collector/tests), for example:

```python
"""Unit tests for the cloc source."""

from ...source_collector_test_case import SourceCollectorTestCase


class ClocLOCTest(SourceCollectorTestCase):
    """Unit tests for the cloc loc collector."""

    SOURCE_TYPE = "cloc"
    METRIC_TYPE = "loc"

    async def test_loc(self):
        """Test that the number of lines is returned."""
        cloc_json = {
            "header": {}, "SUM": {},  # header and SUM are not used
            "Python": {"nFiles": 1, "blank": 5, "comment": 10, "code": 60},
            "JavaScript": {"nFiles": 1, "blank": 2, "comment": 0, "code": 30}}
        response = await self.collect(get_request_json_return_value=cloc_json)
        self.assert_measurement(response, value="90", total="100")
```

Note that the `ClocTest` class is a subclass of `SourceCollectorTestCase` which creates a source and metric for us, specified using `SOURCE_TYPE` and `METRIC_TYPE`, and provides us with helper methods to make it easier to mock sources (`SourceCollectorTestCase.collect()`) and test results (`SourceCollectorTestCase.assert_measurement()`).

In the case of collectors that use files as source, also add an example file to the [test data component](software.md#test-data).

To run the unit tests:

```console
cd components/collector
ci/unittest.sh
```

You should get 100% line and branch coverage.

###### Running quality checks

To run the quality checks:

```console
cd components/collector
ci/quality.sh
```

Because the source collector classes register themselves (see [`SourceCollector.__init_subclass__()`](https://github.com/ICTU/quality-time/blob/master/components/collector/src/base_collectors/source_collector.py)), [Vulture](https://github.com/jendrikseipp/vulture) will think the new source collector subclass is unused:

```console
ci/quality.sh
src/source_collectors/file_source_collectors/cloc.py:26: unused class 'ClocLOC' (60% confidence)
```

Add `Cloc*` to the `NAMES_TO_IGNORE` in [`components/collector/ci/quality.sh`](https://github.com/ICTU/quality-time/blob/master/components/collector/ci/quality.sh) to suppress Vulture's warning.

## Testing

This section assumes you have created a Python virtual environment, activated it, and installed the requirements for each Python component and that you installed the requirements for the frontend component, as described [above](#developing).

### Unit tests

To run the unit tests and measure unit test coverage of the backend components (this assumes you have created a Python virtual environment, activated it, and installed the requirements as described [above](#developing)):

```console
cd components/api_server  # or components/collector, components/notifier, components/shared_code
ci/unittest.sh
```

To run the frontend unit tests:

```console
cd compontents/frontend
npm run test
```

### Quality checks

To run ruff, mypy, and some other security and quality checks on the backend components:

```console
cd components/api_server  # or components/collector, components/notifier, components/shared_code
ci/quality.sh
```

### Feature tests

The feature tests currently test all features through the API served by the API-server. They touch all components except the frontend, the collector, and the notifier. To run the feature tests, invoke this script, it will build and start all the necessary components, run the tests, and gather coverage information:

```console
tests/feature_tests/ci/test.sh
```

The `test.sh` shell script will start a server under coverage and then run the [feature tests](https://github.com/ICTU/quality-time/tree/master/tests/feature_tests).

It's also possible to run a subset of the feature tests by passing the feature file as argument:

```console
tests/feature_tests/ci/test.sh tests/feature_tests/features/metric.feature
```

### Application tests

The application tests in theory test all components through the frontend, but unfortunately the number of tests is too small to meet that goal. To run the application tests, start all components and then start the tests:

```console
docker-compose up -d
docker run -it -w `pwd` -v `pwd`:`pwd` --network=container:qualitytime_www_1 python:3.12.2-bookworm tests/application_tests/ci/test.sh
```

## Documentation and changelog

The documentation is written in Markdown files and published on [Read the Docs](https://quality-time.readthedocs.io/en/latest/).

To generate the documentation locally:

```console
cd docs
python3 -m venv venv
. venv/bin/activate  # on Windows: venv\Scripts\activate
ci/pip-install.sh
make html
open build/html/index.html
```

`make html` also generates the `docs/src/reference.md` reference manual, containing an overview of all subjects, metrics, and sources.

To check the correctness of the links:

```console
make linkcheck
```

## Releasing

### Preparation

Make sure the release folder is the current directory, and you have the dependencies for the release script installed:

```console
cd release
python3 -m venv venv
. venv/bin/activate
ci/pip-install.sh
```

Run the release script with `--help` to show help information, including the current release.

```console
python release.py --help
```

### Decide the release type

*Quality-time* adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html), so first you need to decide on the type of release you want to create:

- Create a **major** release if the next release contains backwards incompatible changes, and optionally other changes and bug fixes.
- Create a **minor** release if the next release contains non-breaking changes, and optionally bug fixes.
- Create a **patch** release if the next release contains bug fixes only.

If you want to test the release (for example, deploy it to a test environment, or roll out a release to early adopters), it's possible to create a **release candidate** for a major, minor, or patch release.

```{important}
To determine whether a release is major, minor, or patch, compare the changes to the [previous most recent release](changelog.md), excluding release candidates.
```

### Determine the version bump

Having decided on the release type, there are the following possibilities for the version bump argument that you will be passing to the release script:

- If the current release is a release candidate,
  - and you want to create another release candidate, use: `rc`. If the current release is e.g. v3.6.1-rc.0, this will bump the version to v3.6.1-rc.1.
  - and the next release will not be, use: `drop-rc`. If the current release is e.g. v3.6.1-rc.0, this will bump the version to v3.6.1.
  - and changes have been made since the previous release candidate that impact the release type, use: `rc-major`, `rc-minor`, or `rc-patch`. If the current release is e.g. v3.6.1-rc.0, using `rc-minor` will bump the version to v3.7.0-rc.0.
- If the current release is not a release candidate:
  - and you want to create a release candidate, use: `rc-major`, `rc-minor`, or `rc-patch`. If the current release is e.g. v3.6.1, using `rc-minor` will bump the version to v3.7.0-rc.0.
  - and you don't want to create a release candidate, use: `major`, `minor`, or `patch`. If the current release is e.g. v3.6.1, using `minor` will bump the version to v3.7.0.

### Check the preconditions

The release script will check a number of preconditions before actually creating the release. To check the preconditions
without releasing, invoke the release script with the version bump as determined:

```console
python release.py --check-preconditions-only <bump>  # Where bump is major, minor, patch, rc-major, rc-minor, rc-patch, rc, or drop-rc
```

If everything is ok, there is no output, and you can proceed creating the release. Otherwise, the release script will list the preconditions that have not been met and need fixing before you can create the release.

### Create the release

To release *Quality-time*, issue the release command (in the release folder) using the type of release you picked:

```console
python release.py <bump>  # Where bump is major, minor, patch, rc-major, rc-minor, rc-patch, rc, or drop-rc
```

If all preconditions are met, the release script will bump the version numbers, update the change history, commit the changes, push the commit, tag the commit, and push the tag to GitHub. The [GitHub Actions release workflow](https://github.com/ICTU/quality-time/actions/workflows/release.yml) will then build the Docker images and push them to [Docker Hub](https://hub.docker.com/search?type=image&q=ictu/quality-time). It will also create an {index}`Software Bill of Materials (SBOM) <Software Bill of Materials (SBOM)>` for the release, which can be found under the "Artifacts" header of the workflow run.

The Docker images are `quality-time_database`, `quality-time_renderer`, `quality-time_api_server`, `quality-time_collector`, `quality-time_notifier`, `quality-time_proxy`, `quality-time_testldap`, and `quality-time_frontend`. The images are tagged with the version number. We don't use the `latest` tag.

## Maintenance

### Python and JavaScript dependencies

Keeping dependencies up-to-date is an important aspect of software maintenance. Python (pip) and JavaScript (npm) dependencies are kept up-to-date via the [Dependabot GitHub action](https://github.com/ICTU/quality-time/blob/master/.github/dependabot.yml).

For Python, we follow the [dependency management practice described by James Bennett](https://www.b-list.org/weblog/2022/may/13/boring-python-dependencies/), to a large extent.

### Docker images

Base images used in the Docker containers, and additionally installed software, need to be upgraded by hand from time to time. These are:

- [API-server](https://github.com/ICTU/quality-time/blob/master/components/api_server/Dockerfile): the Python base image.
- [Collector](https://github.com/ICTU/quality-time/blob/master/components/collector/Dockerfile): the Python base image.
- [Notifier](https://github.com/ICTU/quality-time/blob/master/components/notifier/Dockerfile): the Python base image.
- [Frontend](https://github.com/ICTU/quality-time/blob/master/components/frontend/Dockerfile): the Node base image, the curl version, the npm version, and the serve version.
- [Database](https://github.com/ICTU/quality-time/blob/master/components/database/Dockerfile): the MongoDB base image.
- [Proxy](https://github.com/ICTU/quality-time/blob/master/components/proxy/Dockerfile): the Nginx base image.
- [Renderer](https://github.com/ICTU/quality-time/blob/master/components/renderer/Dockerfile): the Node base image, the curl version, the Chromium version, and the npm version.
- [Test data](https://github.com/ICTU/quality-time/blob/master/components/testdata/Dockerfile): the Python base image.
- Container images directly specified in compose files used for [development](https://github.com/ICTU/quality-time/blob/master/docker/docker-compose.override.yml) and [continuous integration](https://github.com/ICTU/quality-time/blob/master/docker/docker-compose.ci.yml): `mongo-express`, `ldap`, `phpldapadmin`, and `selenium`.
