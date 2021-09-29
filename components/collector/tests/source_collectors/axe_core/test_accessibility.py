"""Unit tests for the Axe-core accessibility collector."""

import json

from collector_utilities.functions import md5_hash

from .base import AxeCoreTestCase


class AxeCoreAccessibilityTest(AxeCoreTestCase):
    """Unit tests for the Axe-core collector for accessibility violations."""

    METRIC_TYPE = "accessibility"

    def setUp(self):
        """Extend to set up test data."""
        super().setUp()
        self.tested_url = "https://tested_url"
        self.json = dict(
            url=self.tested_url,
            violations=[
                dict(
                    id="aria-input-field-name",
                    description="description1",
                    helpUrl="https://help1",
                    tags=["cat.color", "wcag2aa", "wcag143"],
                    nodes=[dict(impact="serious", html="html1")],
                ),
                dict(
                    id="aria-hidden-focus",
                    description="description2",
                    helpUrl="https://help2",
                    nodes=[dict(impact="moderate", html="html2")],
                ),
            ],
            passes=[
                dict(
                    id="aria-hidden-body",
                    impact=None,
                    tags=["cat.aria", "wcag2a", "wcag412"],
                    description="Ensures aria-hidden='true' is not present on the document body.",
                    help="aria-hidden='true' must not be present on the document body",
                    helpUrl="https://dequeuniversity.com/rules/axe/4.1/aria-hidden-body?application=axeAPI",
                    nodes=[dict(impact=None, html="<body>")],
                ),
            ],
            inapplicable=[
                dict(
                    id="aria-allowed-attr",
                    impact=None,
                    tags=["cat.aria", "wcag2a", "wcag412"],
                    description="Ensures ARIA attributes are allowed for an element's role",
                    help="Elements must only use allowed ARIA attributes",
                    helpUrl="https://dequeuniversity.com/rules/axe/4.1/aria-allowed-attr?application=axeAPI",
                    nodes=[],
                ),
            ],
        )
        self.expected_entities = [
            {
                "description": "description1",
                "element": "html1",
                "help": "https://help1",
                "impact": "serious",
                "page": self.tested_url,
                "url": self.tested_url,
                "violation_type": "aria-input-field-name",
                "result_type": "violations",
                "tags": "cat.color, wcag143, wcag2aa",
            },
            {
                "description": "description2",
                "element": "html2",
                "help": "https://help2",
                "impact": "moderate",
                "page": self.tested_url,
                "url": self.tested_url,
                "violation_type": "aria-hidden-focus",
                "result_type": "violations",
                "tags": "",
            },
        ]
        self.set_expected_entity_keys()

    def set_expected_entity_keys(self):
        """Update the keys of the expected entities."""
        for entity in self.expected_entities:
            values = [str(value) for key, value in entity.items() if key not in {"key", "result_type", "tags"}]
            entity["key"] = md5_hash(",".join(values))

    async def test_nr_of_issues(self):
        """Test that the number of issues is returned."""
        response = await self.collect(get_request_json_return_value=self.json)
        self.assert_measurement(response, value="2", entities=self.expected_entities)

    async def test_no_issues(self):
        """Test zero issues."""
        self.json["violations"] = []
        response = await self.collect(get_request_json_return_value=self.json)
        self.assert_measurement(response, value="0", entities=[])

    async def test_filter_by_impact(self):
        """Test that violations can be filtered by impact level."""
        self.set_source_parameter("impact", ["serious", "critical"])
        response = await self.collect(get_request_json_return_value=self.json)
        self.assert_measurement(response, value="1")

    async def test_filter_by_tag_include(self):
        """Test that violations can be filtered by tag."""
        self.set_source_parameter("tags_to_include", ["wcag2aa"])
        response = await self.collect(get_request_json_return_value=self.json)
        self.assert_measurement(response, value="1", entities=[self.expected_entities[0]])

    async def test_filter_by_tag_ignore(self):
        """Test that violations can be filtered by tag."""
        self.set_source_parameter("tags_to_ignore", ["wcag2aa"])
        response = await self.collect(get_request_json_return_value=self.json)
        self.assert_measurement(response, value="1", entities=[self.expected_entities[1]])

    async def test_zipped_json(self):
        """Test that a zip archive with JSON files is processed correctly."""
        self.set_source_parameter("url", "axe.zip")
        zipfile = self.zipped_report(*[(f"axe{index}.json", json.dumps(self.json)) for index in range(2)])
        response = await self.collect(get_request_content=zipfile)
        self.assert_measurement(response, value="2", entities=self.expected_entities)  # Duplicates are discarded

    async def test_json_with_only_violations(self):
        """Test that a JSON file with just a list of violations works."""
        for entity in self.expected_entities:
            entity["page"] = ""
            entity["url"] = ""
        self.set_expected_entity_keys()
        response = await self.collect(get_request_json_return_value=self.json["violations"])
        self.assert_measurement(response, value="2", entities=self.expected_entities)

    async def test_json_with_nested_lists_with_only_violations(self):
        """Test that a JSON file with a nested list of violations works."""
        for entity in self.expected_entities:
            entity["page"] = ""
            entity["url"] = ""
        self.set_expected_entity_keys()
        response = await self.collect(get_request_json_return_value=[self.json["violations"]])
        self.assert_measurement(response, value="2", entities=self.expected_entities)

    async def test_json_with_list_of_result_type_dicts(self):
        """Test that a JSON file with a list of result type dicts works."""
        self.set_expected_entity_keys()
        response = await self.collect(get_request_json_return_value=[self.json])
        self.assert_measurement(response, value="2", entities=self.expected_entities)

    async def test_result_type_parameter(self):
        """Test that other result types besides violations can be counted as well."""
        self.set_source_parameter("result_types", ["violations", "passes"])
        self.expected_entities.append(
            dict(
                description="Ensures aria-hidden='true' is not present on the document body.",
                element="<body>",
                help="https://dequeuniversity.com/rules/axe/4.1/aria-hidden-body?application=axeAPI",
                impact=None,
                page=self.tested_url,
                url=self.tested_url,
                result_type="passes",
                tags="cat.aria, wcag2a, wcag412",
                violation_type="aria-hidden-body",
            )
        )
        self.set_expected_entity_keys()
        response = await self.collect(get_request_json_return_value=self.json)
        self.assert_measurement(response, value="3", entities=self.expected_entities)

    async def test_result_type_without_nodes(self):
        """Test that result types without nodes can be counted as well."""
        self.set_source_parameter("result_types", ["violations", "inapplicable"])
        self.expected_entities.append(
            dict(
                description="Ensures ARIA attributes are allowed for an element's role",
                element=None,
                help="https://dequeuniversity.com/rules/axe/4.1/aria-allowed-attr?application=axeAPI",
                impact=None,
                page=self.tested_url,
                url=self.tested_url,
                result_type="inapplicable",
                tags="cat.aria, wcag2a, wcag412",
                violation_type="aria-allowed-attr",
            )
        )
        self.set_expected_entity_keys()
        response = await self.collect(get_request_json_return_value=self.json)
        self.assert_measurement(response, value="3", entities=self.expected_entities)
