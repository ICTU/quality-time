"""npm source."""

from ..meta.source import Source
from ..parameters import access_parameters


NPM = Source(
    name="npm",
    description="npm is a package manager for the JavaScript programming language.",
    documentation=dict(
        dependencies="""````{tip}
To generate the list of outdated dependencies, run:
```bash
npm outdated --all --long --json > npm-outdated.json
```
To run `npm outdated` with Docker, use:
```bash
docker run --rm -v "$SRC":/work -w /work node:16.9 npm outdated --all --long --json > outdated.json"
```
````
"""
    ),
    url="https://docs.npmjs.com/",
    parameters=access_parameters(
        ["dependencies"],
        source_type="npm 'outdated' report",
        source_type_format="JSON",
        kwargs=dict(url=dict(help_url="https://docs.npmjs.com/cli-commands/outdated.html")),
    ),
    entities=dict(
        dependencies=dict(
            name="dependency",
            name_plural="dependencies",
            attributes=[
                dict(name="Package", key="name"),
                dict(name="Current version", key="current"),
                dict(name="Wanted version", key="wanted"),
                dict(name="Latest version", key="latest"),
            ],
        )
    ),
)
