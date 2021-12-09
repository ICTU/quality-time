import React from 'react';
import { render, screen } from '@testing-library/react';
import { SourceEntityAttribute } from './SourceEntityAttribute';

function renderSourceEntityAttribute(entity, entity_attribute) {
    return render(
        <SourceEntityAttribute entity={entity} entity_attribute={entity_attribute} />
    )
}

it('renders an empty string', () => {
    renderSourceEntityAttribute({ other: "will not be shown"}, { key: "missing" })
    expect(screen.queryAllByText(/will not be shown/).length).toBe(0)
})

it('renders a float', () => {
    renderSourceEntityAttribute({ number: 42.0 }, { key: "number", type: "float"})
    expect(screen.getAllByText(/42/).length).toBe(1)
})

it('renders a zero float', () => {
    renderSourceEntityAttribute({ number: 0.0 }, { key: "number", type: "float"})
    expect(screen.getAllByText(/0/).length).toBe(1)
})

it('renders a datetime', () => {
    renderSourceEntityAttribute({ timestamp: "2021-10-10T10:10:10" }, { key: "timestamp", type: "datetime"})
    expect(screen.getAllByText(/ago/).length).toBe(1)
})

it('renders a date', () => {
    renderSourceEntityAttribute({ date: "2021-10-10T10:10:10" }, { key: "date", type: "date"})
    expect(screen.getAllByText(/ago/).length).toBe(1)
})

it('renders minutes', () => {
    renderSourceEntityAttribute({ duration: "42" }, { key: "duration", type: "minutes"})
    expect(screen.getAllByText(/0:42/).length).toBe(1)
})

it('renders a status icon', () => {
    renderSourceEntityAttribute({ status: "target_met" }, { key: "status", type: "status" })
    expect(screen.getAllByLabelText("Target met").length).toBe(1)
})

it('renders a url', () => {
    renderSourceEntityAttribute({ status: "target_met", url: "https://url" }, { key: "status", type: "status", url: "url" })
    expect(screen.getByLabelText("Target met").closest("a").href).toBe("https://url/")
})

it('renders preformatted text', () => {
    renderSourceEntityAttribute({ text: "text" }, { key: "text", pre: true })
    expect(screen.getByTestId("pre-wrapped")).toBeInTheDocument()
})
