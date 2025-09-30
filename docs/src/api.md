# API

The API of *Quality-time* is used by the frontend, but part of it can also be used for integration purposes.
The public endpoints are documented below.

API documentation can be retrieved via `https://www.quality-time.example.org/api` (all versions, all routes),
`https://www.quality-time.example.org/api/v3` (all routes for a specific version, in this case version 3),
and `https://www.quality-time.example.org/api/v3/<route_fragment>` (all routes matching a specific text fragment).

## Search

For each of the four domain object types a search POST-endpoint is available:

- `api/v3/metric/search`
- `api/v3/report/search`
- `api/v3/source/search`
- `api/v3/subject/search`

Each endpoint expects a JSON with an attribute name and value to search for:

```json
{
    "<attribute_or_parameter_name>": "<value>"
}
```

For example:

```json
{
    "title": "My application"
}
```

The search endpoints can search for exactly one attribute at a time.
The matching is done on the complete value and is case sensitive.

The endpoints return a JSON of the following form if no errors occur:

```json
{
    "domain_object_type": "domain object type passed to the endpoint",
    "ok": true,
    "search_query": "query passed to the endpoint",
    "uuids": ["list of uuids"]
}
```

For example:

```json
{
    "domain_object_type": "metric",
    "ok": true,
    "search_query": {"name": "Metric 1"},
    "uuids": ["e887047a-9ae5-41c2-8fc2-bd9a767420dc"]
}
```

If something goes wrong, an error response is returned:

```json
{
    "domain_object_type": "metric",
    "error": "error message",
    "search_query": {"name": "Metric 1"},
    "ok": false
}
```

The `search_query` is not included in the error response if parsing the search query parameters fails.

## Export to PDF

If the PDF report needs to be downloaded programmatically, e.g. for inclusion in a release package,
use the endpoint: `https://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf`.
No authorization is needed for this endpoint.

The `report_uuid` is the unique identifier that *Quality-time* assigns to a report.
It can be found by navigating to a report in the browser and looking for the `report_uuid` in the address bar.
For example, when the URL in the browser's address bar is `https://www.quality-time.example.org/f1d0e056-2440-43bd-b640-f6753ccf4496?hidden_columns=comment`,
the part between the last slash and the question mark is the `report_uuid`.

To hide metrics that do not need any action, set the `metrics_to_hide` parameter to `no_action_required`,
i.e. `https://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?metrics_to_hide=no_action_required`.
To hide all metrics and only export the report dashboard to PDF, set the `metrics_to_hide` parameter to `all`.

To hide columns from the report, set the `hidden_columns` parameter, for example `https://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?hidden_columns=target,comment`.
Possible options are `trend`, `status`, `measurement`, `delta`, `target`, `unit`, `source`, `time_left`, `overrun`, `comment`, `issues`, and `tags`.

To hide tags from the report, set the `hidden_tags` parameter, for example `https://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?hidden_tags=security,usability`.

To expand metrics and set the active tab of the metric detail information, add the `tabs` parameter, i.e. `https://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?tabs=<metric_uuid>:<tab_index>,<metric_uuid>:<tab_index>,...`.
The metric UUID can be found by navigating to a report in the browser, expanding the metric, and looking for the `tabs` parameter in the address bar.
For example, when the URL in the browser's address bar is `https://www.quality-time.example.org/1d0e056-2440-43bd-b640-f6753ccf4496?tabs=d4c0dea1-b072-417f-804e-6045544748db:0`,
the part between the equal sign and the colon is the metric UUID of the expanded metric.
The number after the colon is the number of the active tab, e.g. 0 is the metrics configuration tab, 1 is the source configuration tab, 2 is the trend graph, etc.

To show the measurement trend, add the `nr_dates` parameter and set it to more than 1, for example `https://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?nr_dates=5`.
The maximum supported value is 7 dates.

To change the time between dates shown, use the `date_interval` parameter.
The interval should be an integer and can have the value 1, 7, 14, 21, or 28.
For example, for example `https://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?date_interval=7`.

To add issue attributes to the exported report, set the `show_issue_summary`, `show_issue_creation_date`, and/or `show_issue_update_date` parameters to `true`.
For example, `https://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?show_issue_summary=true`.

To export an older version of a report, add the `report_date` parameter with a date value in ISO-format (YYYY-MM-DD), for example `https://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?report_date=2020-09-01`.

To set the locale of the exported report, use the `language` parameter with a language code, for example `https://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?language=nl-NL`. Note that the language of the report is always English, the given locale is only used to change the date format. Unfortunately, only English and Dutch are currently supported, see [https://github.com/ICTU/quality-time/issues/10710](https://github.com/ICTU/quality-time/issues/10710).

Reports contain the report URL in the footer of the report.
When exporting PDFs manually, the *Quality-time* frontend supplies the report URL to the endpoint.
When using the endpoint directly to export a report to PDF, the report URL needs to be supplied as parameter.
Add the `report_url` parameter with the URL of the report, for example `https://www.quality-time.example.org/api/v3/report/<report_uuid>/pdf?report_url=https://www.quality-time.example.org/<report_uuid>`.

```{tip}
It is also possible to download a PDF version of the reports overview via the API.
Use the endpoint `https://www.quality-time.example.org/api/v3/reports_overview/pdf`.
No authorization is needed for this endpoint.
The parameters for exporting a report, listed above, can also be used when exporting the reports overview.
```

```{index} Export report
```

```{index} Import report
```

## Export and import reports as JSON

*Quality-time* provides functionality for importing and exporting reports in JSON format.
This functionality can be used for backing up reports or for transferring reports from one *Quality-time* instance to another one.
Currently, this functionality is only available via the API, with one endpoint for importing and one for exporting the JSON reports.

A *Quality-time* report in JSON format contains the latest configuration of the report, with all its subjects, metrics and sources.
It does not contain any actual measurements. The credentials of configured sources are encrypted on export to protect sensitive data.

To use the import and export endpoints you need to be authenticated. For example, using curl:

```console
curl --cookie-jar cookie.txt --request POST --header "Content-Type: application/json" --data '{"username": "jadoe", "password": "secret"}' https://quality-time.example.org/api/v3/login
```

Replace the username and password with the username and password you use to login to *Quality-time*.

### Exporting reports

The exporting endpoint is available via `https://quality-time.source.org/api/v3/report/<report-uuid>/json?public_key=<public-key>`.
The exporting endpoint returns JSON content only.

For example, using curl, and assuming you have logged in as shown above:

```console
curl --cookie cookie.txt --output report.json https://quality-time.source.org/api/v3/report/97b2f341-45ce-4f2b-9a71-3675f2f54cf7/json
```

The `report_uuid` is the unique identifier that *Quality-time* assigns to a report.
It can be found by navigating to a report in the browser and looking for the `report_uuid` in the address bar.
For example, when the URL in the browser's address bar is `https://quality-time.source.org/f1d0e056-2440-43bd-b640-f6753ccf4496?hidden_columns=comment`,
the part between the last slash and the question mark is the `report_uuid`.

The {index}`public key <public key>` argument is optional.
If no public key is provided, the public key of the exporting *Quality-time* instance is used for encrypting the source credentials.
If the report needs to be imported in a different *Quality-time* instance, the public key of that instance should be provided.
It can be obtained at `https://quality-time.destination.org/api/v3/public_key`.
The exported JSON report can only be imported into the *Quality-time* whose public key has been used for the encryption of credentials during the export.

The public key endpoint returns a JSON like this:

```json
{
  "public_key": "-----BEGIN PUBLIC KEY-----\nMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAtXvAeTqsgXIb98rGfZDk\n4ZUssjjrMOCOL7xuZh6lYwN41UP0Day78tbzMxCx8mLfT76DckK1xkeGkKpS/UYD\n2ooDXluplRDGxfebZg+qy54toW878rnYe4HJu6YoDaBnthr1Muy9ttHOVB+6ucXY\nX23uzOF6FD4rZZTn4uGpEF9qfpzaVZrSpqWy9YAfZEsNNjqmbPYR+H0WjdihIpgY\n3AabLHdw02VN8cIzgh1ILLPFcBo2CqNWpETNIGdlPORfDiUx6HVxSXt80xwxFpop\n9hXQDuKSDVGlpVl5YKTwRyqEcFvhbTEJ1gJ+FksCRfrZ/hdVlI5mlCyN/gi+k3gO\nErtN0kFlIwCPyLHw5hsi/f8rLGpG1MaXmtI4fBoTbnozwaTcmoO9GO/Ell3ITTBW\nJbS3fSqKDtTU3NhalnJk5h99yQc+tgHIc+y/odKcicTDw5ZvlNIsY/ig6Z1BqYOl\n3FEI9a+I/mhcynSM/30elGsi+j/ZrWyhD6uB3E9+UtL5l7FtDWyIIoE7DaMQJZxg\nDNLCHWKACjjE+Tjr4ExUEgtzcMMmRXL2QZkylxxT9WU0Qe0U3nwJWBj6h+3xJird\npJ3weRfCPwrZ/6SxWE19tmZiynNnvnywxTJKgT15/Qkv1T0QyVCH/UeyxAhAXqYc\nBulld6J57dZwlpfWtf/ua3cCAwEAAQ==\n-----END PUBLIC KEY-----\n"
}
```

To be able to pass the public key as query parameter to the export endpoint, it needs to be encoded. Download the public key as file:

```console
curl --output public_key.json https://quality-time.destination.org/api/v3/public_key
```

And then encode the public key as follows:

```console
python3 -c 'import json; import urllib.parse; key = json.load(open("public_key.json"))["public_key"]; print(urllib.parse.quote_plus(key))'
```

This prints the public key, looking something like:

```console
-----BEGIN+PUBLIC+KEY----- ... encoded public key ... -----END+PUBLIC+KEY-----%0A
```

### Importing reports

The importing endpoint is available via `https://quality-time.destination.org/api/v3/report/import`.
The import endpoint accepts JSON content only.
See the [example reports](https://github.com/ICTU/quality-time/tree/master/components/api_server/src/example-reports) for the format.

For example, using curl, assuming you have logged in as shown above, and that the report filename is `report.json`:

```console
curl --cookie cookie.txt --request POST --header "Content-Type: application/json" --data @report.json https://quality-time.destination.org/api/v3/report/import
```

On success, you'll see a reply like this:

```console
{"ok": true, "new_report_uuid": "97a3e341-44ce-4f2b-4471-36e5f2f34cf6"}
```

On import, all UUIDs contained in the report (UUIDs of the report, subjects, metrics and sources) will be replaced to prevent conflicts if the report already exists.

If the report contains encrypted credentials, the importing *Quality-time* instance will decrypt the credentials using its public key.
Note that if the credentials were encrypted using the public key of a different *Quality-time* instance, an error will occur, and the import will fail.

To allow for seeding a *Quality-time* instance with default reports, imported reports may contain unencrypted credentials.
These unencrypted credentials will be imported unchanged.

### Copying reports from one *Quality-time* instance to another

Tying the previous two sections together, these steps export a report from a source *Quality-time* instance and import it into a destination instance:

```console
# Get the public key of the destination Quality-time
curl --output public_key.json https://quality-time.destination.org/api/v3/public_key
# Encode the public key
python3 -c 'import json; import urllib.parse; key = json.load(open("public_key.json"))["public_key"]; print(urllib.parse.quote_plus(key))'
-----BEGIN+PUBLIC+KEY-----encoded-public-key-----END+PUBLIC+KEY-----%0A
# Log in to the source Quality-time
curl --cookie-jar cookie.txt --request POST --header "Content-Type: application/json" --data '{"username": "jadoe", "password": "secret"}' https://quality-time.source.org/api/v3/login
# Copy the public key and use it in the next line to export the report
curl --cookie cookie.txt --output report.json https://quality-time.source.org/api/v3/report/1352450b-30fa-4a82-aec5-7b5d0017ee13/json?public_key=-----BEGIN+PUBLIC+KEY-----encoded-public-key-----END+PUBLIC+KEY-----%0A
# Log in to the destination Quality-time
curl --cookie-jar cookie.txt --request POST --header "Content-Type: application/json" --data '{"username": "jadoe", "password": "secret"}' https://quality-time.destination.org/api/v3/login
# Import the report in the destination Quality-time
curl --cookie cookie.txt --request POST --header "Content-Type: application/json" --data @report.json https://quality-time.destination.org/api/v3/report/import
```

## Monitoring metric statuses

To enable monitoring metric statuses outside of *Quality-time*, the `api/v3/report/<report_uuid>/metric_status_summary` endpoint can be used.
It returns a JSON response for the specified report in the following format:

```json
{
    "report_uuid": "xyz",
    "title": "Report title",
    "red": 1,
    "green": 4,
    "other colors": "..."
}
```

The `report_uuid` is the unique identifier that *Quality-time* assigns to a report.
It can be found by navigating to a report in the browser and looking for the `report_uuid` in the address bar.
For example, when the URL in the browser's address bar is `https://www.quality-time.example.org/f1d0e056-2440-43bd-b640-f6753ccf4496?hidden_columns=comment`,
the part between the last slash and the question mark is the `report_uuid`.

## Monitoring *Quality-time* version

To externally retrieve the version of a *Quality-time* instance, the `https://www.quality-time.example.org/api/v3/server` endpoint can be used.
It returns a JSON response of the specified *Quality-time* instance in the following format:

```json
{
  "version": "v5.8.0"
}
```
