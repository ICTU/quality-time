"""npm source."""

from shared_data_model.meta.source import Source
from shared_data_model.parameters import access_parameters

NPM = Source(
    name="npm",
    description="npm is a package manager for the JavaScript programming language.",
    documentation={
        "dependencies": """````{tip}
To generate the list of outdated dependencies, run:
```bash
npm outdated --all --long --json > npm-outdated.json
```
To run `npm outdated` with Docker, use:
```bash
docker run --rm -v "$SRC":/work -w /work node:lts npm outdated --all --long --json > outdated.json"
```
````
""",
    },
    url="https://docs.npmjs.com/",
    parameters=access_parameters(
        ["dependencies"],
        source_type="npm 'outdated' report",
        source_type_format="JSON",
        kwargs={"url": {"help_url": "https://docs.npmjs.com/cli-commands/outdated.html"}},
    ),
    entities={
        "dependencies": {
            "name": "dependency",
            "name_plural": "dependencies",
            "attributes": [
                {"name": "Package", "key": "name"},
                {"name": "Current version", "key": "current"},
                {"name": "Wanted version", "key": "wanted"},
                {"name": "Latest version", "key": "latest"},
            ],
        },
    },
)
