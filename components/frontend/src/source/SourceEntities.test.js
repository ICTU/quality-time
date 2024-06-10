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
                    attributes: [
                        { key: "integer", type: "integer", name: "integer" },
                        {
                            key: "integer_percentage",
                            type: "integer_percentage",
                            name: "int percentage",
                        },
                        { key: "float", type: "float", name: "float" },
                        { key: "text", type: "text", name: "text", help: "help text" },
                        { key: "rightalign", type: "text", name: "rightalign", alignment: "right" },
                        { key: "date", type: "date", name: "date only" },
                        { key: "datetime", type: "datetime", name: "datetime" },
                        { key: "minutes", type: "minutes", name: "minutes" },
                    ],
                },
            },
        },
    },
}

const metric = {
    type: "metric_type",
    sources: {
        source_uuid: {
            type: "source_type",
        },
    },
}

const source = {
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

function renderSourceEntities() {
    render(
        <DataModel.Provider value={dataModel}>
            <SourceEntities metric={metric} report={{ issue_tracker: null }} source={source} />
        </DataModel.Provider>,
    )
}

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
    await userEvent.hover(screen.queryByRole("tooltip", { name: /help/ }))
    await waitFor(() => {
        expect(screen.queryByText(/help text/)).not.toBe(null)
    })
})
