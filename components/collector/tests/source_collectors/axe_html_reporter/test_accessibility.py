"""Unit tests for the Axe HTML reporter accessibility collector."""

from collector_utilities.functions import md5_hash

from ..source_collector_test_case import SourceCollectorTestCase


class AxeHTMLAccessibilityTest(SourceCollectorTestCase):
    """Unit tests for the Axe HTML reporter collector for accessibility violations."""

    METRIC_TYPE = "accessibility"
    SOURCE_TYPE = "axe_html_reporter"

    def setUp(self):
        """Extend to set up test data."""
        super().setUp()
        self.html = """
<div class="violationNode">
    <table>
        <tbody>
            <tr>
                <td>1</td>
                <td>
                    <p><strong>Element location</strong></p>
                    <pre><code class="css text-wrap">#from0</code></pre>
                    <p><strong>Element source</strong></p>
                    <pre><code class="html text-wrap">&lt;input type&#x3D;&quot;text&quot; value&#x3D;&quot;&quot; class&#x3D;&quot;city-input ac_input ui-autocomplete-input&quot; autocomplete&#x3D;&quot;off&quot; id&#x3D;&quot;from0&quot; name&#x3D;&quot;from0&quot; tabindex&#x3D;&quot;1&quot; role&#x3D;&quot;textbox&quot; aria-autocomplete&#x3D;&quot;list&quot; aria-haspopup&#x3D;&quot;true&quot;&gt;</code></pre>
                </td>
                <td>
                    <div class="wrapBreakWord">
                        <p>Fix any of the following:</p>
                        <ul class="text-muted">
                            <li>  Element has a tabindex greater than 0</li>
                        </ul>
                    </div>
                </td>
            </tr>
        </tbody>
    </table>
</div>"""
        self.expected_entities = [
            {
                "description": "Fix any of the following: Element has a tabindex greater than 0",
                "element": """Element location #from0 Element source <input type="text" value="" class="city-input ac_input ui-autocomplete-input" autocomplete="off" id="from0" name="from0" tabindex="1" role="textbox" aria-autocomplete="list" aria-haspopup="true">""",
            },
        ]
        self.set_expected_entity_keys()

    def set_expected_entity_keys(self):
        """Update the keys of the expected entities."""
        for entity in self.expected_entities:
            values = [str(value) for value in entity.values()]
            entity["key"] = md5_hash(",".join(values))

    async def test_nr_of_issues(self):
        """Test that the number of issues is returned."""
        response = await self.collect(get_request_text=self.html)
        self.assert_measurement(response, value="1", entities=self.expected_entities)

    '''
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
    '''
