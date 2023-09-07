"""pip source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Entity, EntityAttribute
from shared_data_model.meta.source import Source
from shared_data_model.parameters import access_parameters

PIP = Source(
    name="pip",
    description="pip is the package installer for Python. You can use pip to install packages from the Python Package "
    "Index and other indexes.",
    documentation={
        "dependencies": """````{tip}
To generate the list of outdated packages in JSON format, run:
```bash
python -m pip list --outdated --format=json > pip-outdated.json
```
````""",
    },
    url=HttpUrl("https://pip.pypa.io/en/stable/"),
    parameters=access_parameters(
        ["dependencies"],
        source_type="pip 'outdated' report",
        source_type_format="JSON",
        kwargs={"url": {"help_url": HttpUrl("https://pip.pypa.io/en/stable/cli/pip_list/")}},
    ),
    entities={
        "dependencies": Entity(
            name="dependency",
            name_plural="dependencies",
            attributes=[
                EntityAttribute(name="Package", key="name", url="homepage"),
                EntityAttribute(name="Current version", key="version"),
                EntityAttribute(name="Latest version", key="latest"),
            ],
        ),
    },
)
