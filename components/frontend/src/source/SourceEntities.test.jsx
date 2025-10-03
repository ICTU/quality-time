import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { createTestableSettings } from "../__fixtures__/fixtures"
import { DataModel } from "../context/DataModel"
import {
    clickText,
    expectLabelText,
    expectNoAccessibilityViolations,
    expectNoText,
    expectText,
    expectTextAfterWait,
} from "../testUtils"
import { SourceEntities } from "./SourceEntities"

const dataModel = {
    sources: {
        source_type: {
            entities: {
                metric_type: {
                    name: "entity name",
                    name_plural: "entities",
                    attributes: [
                        { key: "integer", type: "integer", name: "integer" },
                        {
                            key: "integer_percentage",
                            type: "integer_percentage",
                            name: "int percentage",
                        },
                        { key: "float", type: "float", name: "float" },
                        { key: "text", name: "text", help: "help" }, // Omit type to cover missing type scenario
                        { key: "rightalign", type: "text", name: "rightalign", alignment: "right" },
                        { key: "date", type: "date", name: "date only" },
                        { key: "datetime", type: "datetime", name: "datetime" },
                        { key: "minutes", type: "minutes", name: "minutes" },
                    ],
                },
            },
        },
        source_type_without_entities: { name: "Source type without entities" },
    },
    metrics: {
        metric_type: {
            unit: "items",
        },
        metric_type_without_unit: {},
    },
}

const metricFixture = {
    type: "metric_type",
    sources: {
        source_uuid: {
            type: "source_type",
        },
    },
}

const sourceFixture = {
    source_uuid: "source_uuid",
    entities: [
        {
            key: "1",
            first_seen: "2023-07-01",
            integer: "1",
            integer_percentage: "1",
            float: "0.3",
            text: "CCC",
            rightalign: "right aligned",
            date: "01-01-2000",
            datetime: "2000-01-01T10:00:00Z",
            minutes: "1",
        },
        {
            key: "2",
            first_seen: "2023-07-03",
            integer: "42",
            integer_percentage: "42",
            float: "0.2",
            text: "BBB",
            rightalign: "right aligned",
            date: "01-01-2002",
            datetime: "2002-01-01T10:00:00Z",
            minutes: "2",
        },
        {
            key: "3",
            first_seen: "2023-07-02",
            integer: "9",
            integer_percentage: "9",
            float: "0.1",
            text: "AAA",
            rightalign: "right aligned",
            date: "01-01-2001",
            datetime: "2001-01-01T10:00:00Z",
            minutes: "3",
        },
    ],
    entity_user_data: {
        1: { status: "confirmed", status_end_date: "2020-01-01", rationale: "R1" },
        2: { status: "fixed", status_end_date: "2020-01-02", rationale: "R2" },
    },
}

function expectOrder(expected) {
    const rows = screen.getAllByText(/AAA|BBB|CCC/)
    for (let index = 0; index < expected.length; index++) {
        expect(rows[index]).toHaveTextContent(expected[index].repeat(3))
    }
}

function renderSourceEntities({
    loading = "loaded",
    measurements = [{ sources: [sourceFixture] }],
    metric = metricFixture,
} = {}) {
    return render(
        <DataModel.Provider value={dataModel}>
            <SourceEntities
                loading={loading}
                measurements={measurements}
                metric={metric}
                metricUuid="metric_uuid"
                report={{ issue_tracker: null }}
                settings={createTestableSettings()}
                sourceUuid="source_uuid"
            />
        </DataModel.Provider>,
    )
}

it("renders a message if the metric does not support measurement entities", async () => {
    const { container } = renderSourceEntities({
        metric: { type: "metric_type", sources: { source_uuid: { type: "source_type_without_entities" } } },
    })
    expectText(/Measurement details not supported/)
    expectText(/Showing individual items is not supported when using Source type without entities as source./)
    await expectNoAccessibilityViolations(container)
})

it("renders a message if the metric does not support measurement entities and has no unit", async () => {
    const { container } = renderSourceEntities({
        metric: {
            type: "metric_type_without_unit",
            sources: { source_uuid: { type: "source_type_without_entities" } },
        },
    })
    expectText(/Measurement details not supported/)
    expectText(/Showing individual entities is not supported when using Source type without entities as source./)
    await expectNoAccessibilityViolations(container)
})

it("renders a message if the metric does not have measurement entities", async () => {
    const { container } = renderSourceEntities({
        measurements: [{ sources: [{ source_uuid: "source_uuid", entities: [] }] }],
    })
    expectText(/Measurement details not available/)
    await expectNoAccessibilityViolations(container)
})

it("renders a message if the measurements failed to load", async () => {
    const { container } = renderSourceEntities({ loading: "failed" })
    expectText(/Loading measurements failed/)
    await expectNoAccessibilityViolations(container)
})

it("renders a placeholder while the measurements are loading", async () => {
    const { container } = renderSourceEntities({ loading: "loading" })
    expect(container.firstChild.className).toContain("MuiSkeleton-rectangular")
    expectNoText("AAA")
    await expectNoAccessibilityViolations(container)
})

it("renders a message if there are no measurements", async () => {
    const { container } = renderSourceEntities({ measurements: [] })
    expectText(/No measurements/)
    await expectNoAccessibilityViolations(container)
})

it("shows the hide ignored entities button", async () => {
    const { container } = renderSourceEntities()
    expectLabelText(/Hide the 0 entities that have been/)
    await expectNoAccessibilityViolations(container)
})

it("shows the hide ignored entities button with one ignored entity", async () => {
    const fixture = JSON.parse(JSON.stringify(sourceFixture))
    fixture.entity_user_data["2"].status_end_date = "3000-01-01"
    const { container } = renderSourceEntities({ measurements: [{ sources: [fixture] }] })
    expectLabelText(/Hide the 1 entity name that has been/)
    await expectNoAccessibilityViolations(container)
})

it("shows the hide ignored entities button with two ignored entities", async () => {
    const fixture = JSON.parse(JSON.stringify(sourceFixture))
    fixture.entity_user_data["1"].status = "false_positive"
    fixture.entity_user_data["1"].status_end_date = "3000-01-01"
    fixture.entity_user_data["2"].status_end_date = "3000-01-01"
    const { container } = renderSourceEntities({ measurements: [{ sources: [fixture] }] })
    expectLabelText(/Hide the 2 entities that have been/)
    await expectNoAccessibilityViolations(container)
})

it("shows the show ignored entities button", async () => {
    const fixture = JSON.parse(JSON.stringify(sourceFixture))
    fixture.entity_user_data["2"].status_end_date = "3000-01-01"
    const { container } = renderSourceEntities({ measurements: [{ sources: [fixture] }] })
    const hideEntitiesTooltip = screen.getByLabelText(/Hide the 1 entity name that has been/)
    await userEvent.click(hideEntitiesTooltip.firstChild) // Get the button inside the tooltip
    expect(hideEntitiesTooltip).toHaveAccessibleName(/Show the 1 entity name that has been/)
    await expectNoAccessibilityViolations(container)
})

async function expectColumnIsSortedCorrectly(header, ascending) {
    const { container } = renderSourceEntities()
    expectOrder(["C", "B", "A"]) // Initial order
    clickText(header)
    expectOrder(ascending)
    await expectNoAccessibilityViolations(container)
    clickText(header)
    expectOrder(ascending.toReversed())
    await expectNoAccessibilityViolations(container)
    clickText(header)
    expectOrder(ascending)
}

it("sorts the entities by status", async () => {
    await expectColumnIsSortedCorrectly(/Entity name status/, ["C", "B", "A"])
})

it("sorts the entities by status end date", async () => {
    await expectColumnIsSortedCorrectly(/Status end date/, ["A", "C", "B"])
})

it("sorts the entities by status rationale", async () => {
    await expectColumnIsSortedCorrectly(/Status rationale/, ["A", "C", "B"])
})

it("sorts the entities by first seen date", async () => {
    await expectColumnIsSortedCorrectly(/first seen/, ["C", "A", "B"])
})

it("sorts the entities by integer", async () => {
    await expectColumnIsSortedCorrectly(/integer/, ["C", "A", "B"])
})

it("sorts the entities by integer percentage", async () => {
    await expectColumnIsSortedCorrectly(/int percentage/, ["C", "A", "B"])
})

it("sorts the entities by float", async () => {
    await expectColumnIsSortedCorrectly(/float/, ["A", "B", "C"])
})

it("sorts the entities by text", async () => {
    await expectColumnIsSortedCorrectly(/text/, ["A", "B", "C"])
})

it("sorts the entities by date", async () => {
    await expectColumnIsSortedCorrectly(/date only/, ["C", "A", "B"])
})

it("sorts the entities by datetime", async () => {
    await expectColumnIsSortedCorrectly(/datetime/, ["C", "A", "B"])
})

it("sorts the entities by minutes", async () => {
    await expectColumnIsSortedCorrectly(/minutes/, ["C", "B", "A"])
})

it("shows help", async () => {
    renderSourceEntities()
    await userEvent.hover(screen.queryByTestId("HelpIcon"))
    await expectTextAfterWait(/help/)
})
