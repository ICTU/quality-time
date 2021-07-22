# *Quality-time* test data

This component contains test data for the example reports.

## Running the test data component

The test data component is started as part of the [docker composition](../../docker/docker-compose.override.yml) for development, see the [developer manual](../../docs/DEVELOP.md).

To serve the test data locally, you can also simply start a webserver, e.g.:

```console
python3 -m http.server
```

## Adding test data

Add the example file(s) to the [test data reports](reports) and update one or more of the [example reports](../server/src/data/example-reports) in the server component.

## Acknowledgements

- `cobertura.xml` was copied from [https://github.com/Bachmann1234/diff_cover/blob/master/diff_cover/tests/fixtures/dotnet_coverage.xml](https://github.com/Bachmann1234/diff_cover/blob/master/diff_cover/tests/fixtures/dotnet_coverage.xml).
- `testng-results.xml` was copied from [https://github.com/richie-b/AtnApiTest/blob/master/test-output/testng-results.xml](https://github.com/richie-b/AtnApiTest/blob/master/test-output/testng-results.xml).
