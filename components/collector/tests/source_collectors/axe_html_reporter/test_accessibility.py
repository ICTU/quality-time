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
            <div class="card violationCard">
                <div class="card-body">
                    <div class="violationCardLine">
                        <h5 class="card-title violationCardTitleItem">
                            <a id="1">1.</a> &lt;html&gt; element must have a lang attribute
                        </h5>
                        <a
                            href="https:&#x2F;&#x2F;dequeuniversity.com&#x2F;rules&#x2F;axe&#x2F;3.5&#x2F;html-has-lang?application&#x3D;axeAPI"
                            target="_blank"
                            class="card-link violationCardTitleItem learnMore"
                            >Learn more</a
                        >
                    </div>
                    <div class="violationCardLine">
                        <h6 class="card-subtitle mb-2 text-muted">html-has-lang</h6>
                        <h6 class="card-subtitle mb-2 text-muted violationCardTitleItem">
                            WCAG 2 Level A, WCAG 3.1.1
                        </h6>
                    </div>
                    <div class="violationCardLine">
                        <p class="card-text">Ensures every HTML document has a lang attribute</p>
                        <h6 class="card-subtitle mb-2 text-muted violationCardTitleItem">
                            serious
                        </h6>
                    </div>
                    <div class="violationCardLine">
                        <h6 class="card-subtitle mb-2 text-muted violationCardTitleItem">
                            Issue Tags:
                            <span class="badge bg-light text-dark"> cat.language </span>

                            <span class="badge bg-light text-dark"> wcag2a </span>

                            <span class="badge bg-light text-dark"> wcag311 </span>
                        </h6>
                    </div>
                    <div class="violationNode">
                        <table class="table table-sm table-bordered">
                            <thead>
                                <tr>
                                    <th style="width: 2%">#</th>
                                    <th style="width: 49%">Issue Description</th>
                                    <th style="width: 49%">
                                        To solve this violation, you need to...
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>1</td>
                                    <td>
                                        <p><strong>Element location</strong></p>
                                        <pre><code class="css text-wrap">html</code></pre>
                                        <p><strong>Element source</strong></p>
                                        <pre><code class="html text-wrap">&lt;html&gt;</code></pre>
                                    </td>
                                    <td>
                                        <div class="wrapBreakWord">
                                            <p>Fix any of the following:</p>
                                            <ul class="text-muted">
                                                <li>  The &lt;html&gt; element does not have a lang attribute</li>
                                            </ul>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>"""
        self.expected_entities = [
            dict(
                solution="Fix any of the following: The <html> element does not have a lang attribute",
                element="Element location html Element source <html>",
                rule="1. <html> element must have a lang attribute",
                tags=["cat.language", "wcag2a", "wcag311"],
            ),
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
