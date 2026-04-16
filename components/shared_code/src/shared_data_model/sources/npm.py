"""npm source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Entity, EntityAttribute
from shared_data_model.meta.source import Source
from shared_data_model.parameters import MultipleChoiceWithDefaultsParameter, access_parameters

NPM = Source(
    name="npm",
    description="npm is a package manager for the JavaScript programming language.",
    documentation={
        "dependencies": """````{tip}
To generate the list of outdated dependencies, run:
```bash
npm outdated --long --json > npm-outdated.json
```
To run `npm outdated` with Docker, use:
```bash
docker run --rm -v "$SRC":/work -w /work node:lts npm outdated --long --json > outdated.json"
```
````
""",
    },
    url=HttpUrl("https://docs.npmjs.com/"),
    parameters={
        "updates_to_include": MultipleChoiceWithDefaultsParameter(
            name="Updates to include",
            placeholder="all updates",
            help="Limit which updates to include based on the semantic version difference between the current and "
            "latest version. Select 'major' to include updates where the major version changes, 'minor' to include "
            "updates where the major version stays the same but the minor version changes, and 'patch' to include "
            "updates where the major and minor versions stay the same but the patch version changes.",
            values=["major", "minor", "patch"],
            metrics=["dependencies"],
        ),
        **access_parameters(
            ["dependencies"],
            source_type="npm 'outdated' report",
            source_type_format="JSON",
            kwargs={"url": {"help_url": HttpUrl("https://docs.npmjs.com/cli-commands/outdated.html")}},
        ),
    },
    entities={
        "dependencies": Entity(
            name="dependency",
            name_plural="dependencies",
            attributes=[
                EntityAttribute(name="Package", key="name"),
                EntityAttribute(name="Current version", key="current"),
                EntityAttribute(name="Wanted version", key="wanted"),
                EntityAttribute(name="Latest version", key="latest"),
            ],
        ),
    },
)
