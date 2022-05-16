import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { SourceEntities } from './SourceEntities';
import { DataModel } from '../context/DataModel';
import userEvent from '@testing-library/user-event';

const data_model = {
    sources: {
        source_type: {
            entities: {
                metric_type:
                {
                    name: "entity name",
                    attributes: [
                        { key: "integer", type: "integer", name: "integer" },
                        { key: "float", type: "float", name: "float" },
                        { key: "text", type: "text", name: "text", help: "help text" },
                        { key: "rightalign", type: "text", name: "rightalign", alignment: "right" },
                        { key: "date", type: "date", name: "date only" },
                        { key: "datetime", type: "datetime", name: "datetime" },
                        { key: "minutes", type: "minutes", name: "minutes" }
                    ]
                }
            }
        }
    }
}

const metric = {
    type: "metric_type",
    sources: {
        source_uuid: {
            type: "source_type"
        }
    }
}

const source = {
    source_uuid: "source_uuid",
    entities: [
        {
            key: "1",
            integer: "1",
            float: "0.3",
            text: "CCC",
            rightalign: "right aligned",
            date: "01-01-2000",
            datetime: "2000-01-01T10:00:00Z",
            minutes: "1"
        },
        {
            key: "2",
            integer: "3",
            float: "0.2",
            text: "BBB",
            rightalign: "right aligned",
            date: "01-01-2002",
            datetime: "2002-01-01T10:00:00Z",
            minutes: "2"
        },
        {
            key: "3",
            integer: "2",
            float: "0.1",
            text: "AAA",
            rightalign: "right aligned",
            date: "01-01-2001",
            datetime: "2001-01-01T10:00:00Z",
            minutes: "3"
        }
    ]
}

function assertOrder(expected) {
    const rows = screen.getAllByText(/AAA|BBB|CCC/)
    for (let index = 0; index < expected.length; index++) {
        expect(rows[index]).toHaveTextContent(expected[index].repeat(3))
    }
}

it('sorts the entities by status', async () => {
    render(<DataModel.Provider value={data_model}><SourceEntities metric={metric} source={source} /></DataModel.Provider>)
    assertOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/Entity name status/))
    assertOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/Entity name status/))
    assertOrder(["A", "B", "C"])
})

it('sorts the entities by status end date', async () => {
    render(<DataModel.Provider value={data_model}><SourceEntities metric={metric} source={source} /></DataModel.Provider>)
    assertOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/Status end date/))
    assertOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/Status end date/))
    assertOrder(["A", "B", "C"])
})

it('sorts the entities by status rationale', async () => {
    render(<DataModel.Provider value={data_model}><SourceEntities metric={metric} source={source} /></DataModel.Provider>)
    assertOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/Status rationale/))
    assertOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/Status rationale/))
    assertOrder(["A", "B", "C"])
})

it('sorts the entities by integer', async () => {
    render(<DataModel.Provider value={data_model}><SourceEntities metric={metric} source={source} /></DataModel.Provider>)
    assertOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/integer/))
    assertOrder(["C", "A", "B"])
    await userEvent.click(screen.getByText(/integer/))
    assertOrder(["B", "A", "C"])
})

it('sorts the entities by float', async () => {
    render(<DataModel.Provider value={data_model}><SourceEntities metric={metric} source={source} /></DataModel.Provider>)
    assertOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/float/))
    assertOrder(["A", "B", "C"])
    await userEvent.click(screen.getByText(/float/))
    assertOrder(["C", "B", "A"])
})

it('sorts the entities by text', async () => {
    render(<DataModel.Provider value={data_model}><SourceEntities metric={metric} source={source} /></DataModel.Provider>)
    assertOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/text/))
    assertOrder(["A", "B", "C"])
    await userEvent.click(screen.getByText(/text/))
    assertOrder(["C", "B", "A"])
})

it('sorts the entities by date', async () => {
    render(<DataModel.Provider value={data_model}><SourceEntities metric={metric} source={source} /></DataModel.Provider>)
    assertOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/date only/))
    assertOrder(["C", "A", "B"])
    await userEvent.click(screen.getByText(/date only/))
    assertOrder(["B", "A", "C"])
})

it('sorts the entities by datetime', async () => {
    render(<DataModel.Provider value={data_model}><SourceEntities metric={metric} source={source} /></DataModel.Provider>)
    assertOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/datetime/))
    assertOrder(["C", "A", "B"])
    await userEvent.click(screen.getByText(/datetime/))
    assertOrder(["B", "A", "C"])
})

it('sorts the entities by minutes', async () => {
    render(<DataModel.Provider value={data_model}><SourceEntities metric={metric} source={source} /></DataModel.Provider>)
    assertOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/minutes/))
    assertOrder(["C", "B", "A"])
    await userEvent.click(screen.getByText(/minutes/))
    assertOrder(["A", "B", "C"])
})

it('shows help', async () => {
    render(<DataModel.Provider value={data_model}><SourceEntities metric={metric} source={source} /></DataModel.Provider>)
    await userEvent.hover(screen.queryByRole("tooltip", {name: /help/}))
    await waitFor(() => { expect(screen.queryByText(/help text/)).not.toBe(null) })
})
