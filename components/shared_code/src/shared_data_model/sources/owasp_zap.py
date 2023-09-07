"""OWASP ZAP source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute
from shared_data_model.meta.source import Source
from shared_data_model.parameters import (
    MultipleChoiceParameter,
    MultipleChoiceWithAdditionParameter,
    SingleChoiceParameter,
    access_parameters,
)

ALL_OWASP_ZAP_METRICS = ["security_warnings", "source_up_to_dateness", "source_version"]

OWASP_ZAP = Source(
    name="OWASP ZAP",
    description="The OWASP Zed Attack Proxy (ZAP) can help automatically find security vulnerabilities in web "
    "applications while the application is being developed and tested.",
    url=HttpUrl("https://owasp.org/www-project-zap/"),
    parameters={
        "alerts": SingleChoiceParameter(
            name="Count alert types or alert instances",
            short_name="count alert types or instances setting",
            help="Determine whether to count each alert type in the OWASP ZAP report as a security warning or to "
            "count each alert instance (URL).",
            default_value="alert instances",
            values=["alert types", "alert instances"],
            metrics=["security_warnings"],
        ),
        "risks": MultipleChoiceParameter(
            name="Risks",
            help="If provided, only count security warnings with the selected risks.",
            placeholder="all risks",
            values=["informational", "low", "medium", "high"],
            api_values={"informational": "0", "low": "1", "medium": "2", "high": "3"},
            metrics=["security_warnings"],
        ),
        "variable_url_regexp": MultipleChoiceWithAdditionParameter(
            name="Parts of URLs to ignore (regular expressions)",
            short_name="parts of URLs to ignore",
            help="Parts of URLs to ignore can be specified by regular expression. The parts of URLs that match one "
            "or more of the regular expressions are removed. If, after applying the regular expressions, multiple "
            "warnings are the same only one is reported.",
            metrics=["security_warnings"],
        ),
        **access_parameters(ALL_OWASP_ZAP_METRICS, source_type="an OWASP ZAP report", source_type_format="XML"),
    },
    entities={
        "security_warnings": Entity(
            name="security warning",
            attributes=[
                EntityAttribute(name="Warning", key="name"),
                EntityAttribute(
                    name="Risk (Confidence)",
                    key="risk",
                    color={
                        "High (Low)": Color.NEGATIVE,
                        "High (Medium)": Color.NEGATIVE,
                        "High (High)": Color.NEGATIVE,
                        "Medium (Low)": Color.WARNING,
                        "Medium (Medium)": Color.WARNING,
                        "Medium (High)": Color.WARNING,
                    },
                ),
                EntityAttribute(name="Description"),
                EntityAttribute(name="Location", url="uri"),
            ],
        ),
    },
)
