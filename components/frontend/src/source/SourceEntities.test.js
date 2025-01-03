import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { DataModel } from "../context/DataModel"
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
                        { key: "text", name: "text", help: "help text" }, // Omit type to cover missing type scenario
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
                metric_uuid="metric_uuid"
                report={{ issue_tracker: null }}
                source_uuid="source_uuid"
            />
        </DataModel.Provider>,
    )
}

it("renders a message if the metric does not support measurement entities", () => {
    renderSourceEntities({
        metric: { type: "metric_type", sources: { source_uuid: { type: "source_type_without_entities" } } },
    })
    expect(screen.getAllByText(/Measurement details not supported/).length).toBe(1)
    expect(
        screen.getAllByText(
            /Showing individual items is not supported when using Source type without entities as source./,
        ).length,
    ).toBe(1)
})

it("renders a message if the metric does not support measurement entities andhas no unit", () => {
    renderSourceEntities({
        metric: {
            type: "metric_type_without_unit",
            sources: { source_uuid: { type: "source_type_without_entities" } },
        },
    })
    expect(screen.getAllByText(/Measurement details not supported/).length).toBe(1)
    expect(
        screen.getAllByText(
            /Showing individual entities is not supported when using Source type without entities as source./,
        ).length,
    ).toBe(1)
})

it("renders a message if the metric does not have measurement entities", () => {
    renderSourceEntities({ measurements: [{ sources: [{ source_uuid: "source_uuid", entities: [] }] }] })
    expect(screen.getAllByText(/Measurement details not available/).length).toBe(1)
})

it("renders a message if the measurements failed to load", () => {
    renderSourceEntities({ loading: "failed" })
    expect(screen.getAllByText(/Loading measurements failed/).length).toBe(1)
})

it("renders a placeholder while the measurements are loading", () => {
    const { container } = renderSourceEntities({ loading: "loading" })
    expect(container.firstChild.className).toContain("MuiSkeleton-rectangular")
    expect(screen.queryAllByText("AAA").length).toBe(0)
})

it("renders a message if there are no measurements", () => {
    renderSourceEntities({ measurements: [] })
    expect(screen.getAllByText(/No measurements/).length).toBe(1)
})

it("shows the hide ignored entities button", async () => {
    renderSourceEntities()
    const hideEntitiesButton = screen.getAllByRole("button")[0]
    expect(hideEntitiesButton).toHaveAttribute("aria-label", "Hide ignored entities")
})

it("shows the show ignored entities button", async () => {
    renderSourceEntities()
    const hideEntitiesButton = screen.getAllByRole("button")[0]
    await userEvent.click(hideEntitiesButton)
    expect(hideEntitiesButton).toHaveAttribute("aria-label", "Show ignored entities")
})

it("sorts the entities by status", async () => {
    renderSourceEntities()
    expectOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/Entity name status/))
    expectOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/Entity name status/))
    expectOrder(["A", "B", "C"])
})

it("sorts the entities by status end date", async () => {
    renderSourceEntities()
    expectOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/Status end date/))
    expectOrder(["A", "C", "B"])
    await userEvent.click(screen.getByText(/Status end date/))
    expectOrder(["B", "C", "A"])
})

it("sorts the entities by status rationale", async () => {
    renderSourceEntities()
    expectOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/Status rationale/))
    expectOrder(["A", "C", "B"])
    await userEvent.click(screen.getByText(/Status rationale/))
    expectOrder(["B", "C", "A"])
})

it("sorts the entities by first seen date", async () => {
    renderSourceEntities()
    expectOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/first seen/))
    expectOrder(["C", "A", "B"])
    await userEvent.click(screen.getByText(/first seen/))
    expectOrder(["B", "A", "C"])
})

it("sorts the entities by integer", async () => {
    renderSourceEntities()
    expectOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/integer/))
    expectOrder(["C", "A", "B"])
    await userEvent.click(screen.getByText(/integer/))
    expectOrder(["B", "A", "C"])
})

it("sorts the entities by integer percentage", async () => {
    renderSourceEntities()
    expectOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/int percentage/))
    expectOrder(["C", "A", "B"])
    await userEvent.click(screen.getByText(/int percentage/))
    expectOrder(["B", "A", "C"])
})

it("sorts the entities by float", async () => {
    renderSourceEntities()
    expectOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/float/))
    expectOrder(["A", "B", "C"])
    await userEvent.click(screen.getByText(/float/))
    expectOrder(["C", "B", "A"])
})

it("sorts the entities by text", async () => {
    renderSourceEntities()
    expectOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/text/))
    expectOrder(["A", "B", "C"])
    await userEvent.click(screen.getByText(/text/))
    expectOrder(["C", "B", "A"])
})

it("sorts the entities by date", async () => {
    renderSourceEntities()
    expectOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/date only/))
    expectOrder(["C", "A", "B"])
    await userEvent.click(screen.getByText(/date only/))
    expectOrder(["B", "A", "C"])
})

it("sorts the entities by datetime", async () => {
    renderSourceEntities()
    expectOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/datetime/))
    expectOrder(["C", "A", "B"])
    await userEvent.click(screen.getByText(/datetime/))
    expectOrder(["B", "A", "C"])
})

it("sorts the entities by minutes", async () => {
    renderSourceEntities()
    expectOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/minutes/))
    expectOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/minutes/))
    expectOrder(["A", "B", "C"])
})

it("shows help", async () => {
    renderSourceEntities()
    await userEvent.hover(screen.queryByTestId("HelpIcon"))
    await waitFor(() => {
        expect(screen.queryByText(/help text/)).not.toBe(null)
    })
})
