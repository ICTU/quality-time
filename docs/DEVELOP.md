# Developing *Quality-time*

## Table of contents

- [Develop](#develop)
- [Test](#test)
- [Release](#release)
- [Software components](#software-components)
- [Adding metrics and sources](#adding-metrics-and-sources)

## Develop

Follow these instructions to run the software in hot-reload mode for easy development. Prerequisites are Python 3.8 and a recent version of Node.js (we test with the Long Term Support version of Node).

Clone this repository:

```console
git clone git@github.com:ICTU/quality-time.git
```

Open four terminals. In the first one, run the standard containers with docker-compose:

```console
docker-compose up database ldap phpldapadmin mongo-express testdata
```

Mongo-express is served at [http://localhost:8081](http://localhost:8081) and can be used to inspect and edit the database contents.

PHP-LDAP-admin is served at [http://localhost:3890](http://localhost:3890) and can be used to inspect and edit the LDAP database. Click login, check the "Anonymous" box and click "Authenticate" to login.

In the second terminal, run the server:

```console
cd components/server
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python src/quality_time_server.py
```

In the third terminal, run the collector:

```console
cd components/collector
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python src/quality_time_collector.py
```

In the fourth terminal, run the frontend:

```console
cd components/frontend
npm install
npm run start
```

The frontend is served at [http://localhost:3000](http://localhost:3000).

By default, there are three users defined in the LDAP database:

- User `admin` has password `admin`.
- User `Jane Doe` has user id `jadoe` and password `secret`.
- User `John Doe` has user id `jodoe` and password `secret`.

## Test

### Unit tests

To run the unit tests and measure unit test coverage of the backend components:

```console
cd components/server  # or components/collector
ci/unittest.sh
```

To run the frontend unit tests:

```console
cd compontents/frontend
npm run test
```

### Quality checks

To run mypy, pylint, and some other security and quality checks on the backend components:

```console
cd components/server  # or components/collector
ci/quality.sh
```

### Integration tests

To run the integration tests (these currently test all components except the collector), start the following components and then run the feature tests:

```console
docker-compose up -d ldap database renderer www frontend server  # And optionally mongo-express
ci/behave.sh
```

The `behave.sh` shell script will start a server under coverage and then run the behave [feature tests](../tests/features).

## Release

See [Release README](../ci/README.md).

## Software components

![Components](components.png)

*Quality-time* consists of six components. Three standard components:

- A proxy (we use the [ICTU variant of Caddy](https://github.com/ICTU/caddy), but this can be replaced by another proxy if so desired) routing traffic from and to the user's browser,
- A database ([Mongo](https://www.mongodb.com)) for storing reports and measurements,
- A renderer (we use the [ICTU variant of url-to-pdf-api](https://github.com/ICTU/url-to-pdf-api) to export reports to PDF,

And three bespoke components:

- A [frontend](../components/frontend/README.md) serving the React UI,
- A [server](../components/server/README.md) serving the API,
- A [collector](../components/collector/README.md) to collect the measurements from the sources.

In addition, an LDAP server is expected to be available to authenticate users.

For testing purposes there are also [test data](../components/testdata/README.md) and an [LDAP-server](../components/ldap/README.md).

## Adding metrics and sources

*Quality-time* has been designed with the goal of making it easy to add new metrics and sources. The [data model](../components/server/src/data/datamodel.json) specifies all the details about metrics and sources, like the scale and unit of metrics, and the parameters needed for sources. In general, besides changing the data model, no coding is needed to add a new metric, besides augmenting the [collector](../components/collector/README.md) component to parse the source data and optionally adding a logo to the [frontend](../components/frontend/README.md) component.

### Adding new metrics

To add a new metric you need to add a specification of the metric to the [data model](../components/server/src/data/datamodel.json). See the documentation of the [server](../components/server/README.md) component for a description of the data model. Be sure to run the unit tests of the server component after adding a metric to the data model, they check the integrity of the data model. Other than changing the data model, no code changes are needed to support new metrics.

### Adding new sources

#### Adding the new source to the data model

To add a new source you need to add a specification of the source to the [data model](../components/server/src/data/datamodel.json). See the documentation of the [server](../components/server/README.md) component for a description of the data model. Be sure to run the unit tests of the server component after adding a source to the data model, they check the integrity of the data model.

Suppose we want to add [cloc](https://github.com/AlDanial/cloc) as source for the LOC (size) metric and read the size of source code from the JSON file that cloc can produce. We would add a `cloc` source to the data model (see the [data model](../components/server/src/data/datamodel.json) for the complete specification):

```json
{
    "sources": {
        ...
        "cloc": {
            "name": "cloc",
            "description": "cloc is an open-source tool for counting blank lines, comment lines, and physical lines of source code in many programming languages",
            "url": "https://github.com/AlDanial/cloc",
            "parameters": {
                "url": {
                    "name": "URL to a cloc report in JSON format or to a zip with cloc reports in JSON format",
                    "short_name": "URL",
                    "type": "url",
                    "mandatory": true,
                    "default_value": "",
                    "metrics": [
                        "loc"
                    ]
                },
                <...more parameters>
            }
        }
    }
}
```

#### Adding the new source to the collector

To specify how *Quality-time* can collect data from the source, a new subclass of [`SourceCollector`](../components/collector/src/base_collectors/source_collector.py) needs to be created.

Currently, the subclasses of `SourceCollector` are grouped into three modules:

1. [API collectors](../components/collector/src/source_collectors/api_source_collectors) consume an API, e.g. the GitLab API or Azure DevOps API, to collect data,
1. [file collectors](../components/collector/src/source_collectors/file_source_collectors) parse files, e.g. XML or JSON, to collect data,
1. [local collectors](../components/collector/src/source_collectors/local_source_collectors) don't need remote access because they e.g. use a fixed value specified by the user as measurement or the time since a specific date.

Decide on the type of collector you're creating and add a file to the correct module. In the file, create a subclass of `SourceCollector` for each metric that the source can support. For example, if the new source `cloc` supports the metric LOC (size) and the metric source-uo-to-dateness, you would create two subclasses of `SourceCollector`: a `ClocLOC` class a `ClocSourceUpToDateness` class.

To reduce duplication, `SourceCollector` has several abstract subclasses. The class hierarchy is currently as follows:

- `SourceCollector`
  - `UnmergedBranchesSourceCollector`: for sources that collect data for the number of unmerged branches metric
  - `SourceUpToDatenessCollector`: for sources that support the source-up-to-dateness metric
    - `JenkinsPluginSourceUpToDatenessCollector`: for getting the source-up-to-dateness from Jenkins plugins
  - `LocalSourceCollector`: for sources that are local to the collector like fixed numbers and date/times
  - `FileSourceCollector`: for sources that parse files
    - `CSVFileSourceCollector`: for sources that parse CSV files
    - `HTMLFileSourceCollector`: for sources that parse HTML files
    - `JSONFileSourceCollector`: for sources that parse JSON files
    - `XMLFileSourceCollector`: for sources that parse XML files

To support [cloc](https://github.com/AlDanial/cloc) as source for the LOC (size) metric we need to read the size of source code from the JSON file that cloc can produce. We add a `cloc.py` file to the `file collectors` module and in `cloc.py` we create a `ClocLOC` class with `JSONFileSourceCollector` a super class. The only method that needs to be implemented is `_parse_source_responses()` to get the amount of lines from the cloc JSON file. This could be as simple as:

```python
"""cloc metrics collector."""

from typing import Tuple

from collector_utilities.type import Entities, Responses, Value
from base_collectors import JSONFileSourceCollector


class ClocLOC(JSONFileSourceCollector):
    """cloc collector for size/lines of code."""

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        loc = 0
        for response in responses:
            for key, value in (await response.json()).items():
                if key not in ("header", "SUM"):
                    loc += value["code"]
        return str(loc), "100", []
```

Most collector classes are bit more complex than that, because to retrieve the data they have to deal with API's and while parsing the data they have to take parameters into account. See the collector source code for more examples.

##### Unit tests

To test the `ClocLOC` collector class, we add unit tests to the [collector tests package](../components/collector/tests), for example:

```python
"""Unit tests for the cloc source."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class ClocTest(SourceCollectorTestCase):
    """Unit tests for the cloc metrics."""

    async def test_loc(self):
        """Test that the number of lines is returned."""
        cloc_json = {
            "header": {}, "SUM": {},  # header and SUM are not used
            "Python": {"nFiles": 1, "blank": 5, "comment": 10, "code": 60},
            "JavaScript": {"nFiles": 1, "blank": 2, "comment": 0, "code": 30}}
        sources = dict(source_id=dict(type="cloc", parameters=dict(url="https://cloc.json")))
        metric = dict(type="loc", sources=sources, addition="sum")
        response = await self.collect(metric, get_request_json_return_value=cloc_json)
        self.assert_measurement(response, value="90", total="100", entities=[])
```

Note that the `ClocTest` class is a subclass of `SourceCollectorTestCase` which provides us with helper methods to make it easier to mock sources (`SourceCollectorTestCase.collect()`) and test results (`SourceCollectorTestCase.assert_measurement()`).

In the case of file collectors, also add an example file to the [test data component](../components/testdata/README.md).

To run the unit tests:

```console
cd components/collector
ci/unittest.sh
```

You should get 100% line and branch coverage.

##### Quality checks

To run the quality checks:

```console
cd components/collector
ci/quality.sh
```

Because the source collector classes register themselves (see [`SourceCollector.__init_subclass__()`](../components/collector/src/base_collectors/source_collector.py)), [Vulture](https://github.com/jendrikseipp/vulture) will think the new source collector subclass is unused:

```console
ci/quality.sh
src/source_collectors/file_source_collectors/cloc.py:26: unused class 'ClocLOC' (60% confidence)
```

Add "Cloc*" to the `NAMES_TO_IGNORE` in [components/collector/ci/quality.sh](../components/collector/ci/quality.sh) to suppress Vulture's warning.

#### Adding a logo for the new source to the frontend

Add a small png file of the logo in [`components/frontend/src/logos`](../components/frontend/src/logos) and update the [Logo.js](../components/frontend/src/logos/Logo.js) file.
