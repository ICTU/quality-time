import { render, screen } from "@testing-library/react"

import { SourceEntityAttribute } from "./SourceEntityAttribute"

function renderSourceEntityAttribute(entity, entityAttribute) {
    return render(<SourceEntityAttribute entity={entity} entityAttribute={entityAttribute} />)
}

it("renders a short string", () => {
    renderSourceEntityAttribute({ text: "short text" }, { key: "text" })
    expect(screen.queryAllByText(/short text/).length).toBe(1)
})

it("renders a long string", () => {
    const longText = "long text ".repeat(100)
    renderSourceEntityAttribute({ text: longText }, { key: "text" })
    const expectedText = longText.slice(0, 247) + "..."
    expect(screen.queryAllByText(expectedText).length).toBe(1)
})

it("renders an empty string", () => {
    renderSourceEntityAttribute({ other: "will not be shown" }, { key: "missing" })
    expect(screen.queryAllByText(/will not be shown/).length).toBe(0)
})

it("renders a float", () => {
    renderSourceEntityAttribute({ number: 42.0 }, { key: "number", type: "float" })
    expect(screen.getAllByText(/42/).length).toBe(1)
})

it("renders a zero float", () => {
    renderSourceEntityAttribute({ number: 0.0 }, { key: "number", type: "float" })
    expect(screen.getAllByText(/0/).length).toBe(1)
})

it("renders an integer", () => {
    renderSourceEntityAttribute({ number: 42.0 }, { key: "number", type: "integer" })
    expect(screen.getAllByText(/42/).length).toBe(1)
})

it("renders an integer percentage", () => {
    renderSourceEntityAttribute({ number: 42.0 }, { key: "number", type: "integer_percentage" })
    expect(screen.getAllByText(/42%/).length).toBe(1)
})

it("renders a datetime", () => {
    renderSourceEntityAttribute({ timestamp: "2021-10-10T10:10:10" }, { key: "timestamp", type: "datetime" })
    expect(screen.getAllByText(/ago/).length).toBe(1)
})

it("renders a date", () => {
    renderSourceEntityAttribute({ date: "2021-10-10T10:10:10" }, { key: "date", type: "date" })
    expect(screen.getAllByText(/ago/).length).toBe(1)
})

it("renders minutes", () => {
    renderSourceEntityAttribute({ duration: "42" }, { key: "duration", type: "minutes" })
    expect(screen.getAllByText(/42/).length).toBe(1)
})

it("renders a status icon", () => {
    renderSourceEntityAttribute({ status: "target_met" }, { key: "status", type: "status" })
    expect(screen.getAllByLabelText("Target met").length).toBe(1)
})

it("renders a url", () => {
    renderSourceEntityAttribute(
        { status: "target_met", url: "https://url" },
        { key: "status", type: "status", url: "url" },
    )
    expect(screen.getByLabelText("Target met").closest("a").href).toBe("https://url/")
})

it("renders preformatted text", () => {
    renderSourceEntityAttribute({ text: "text" }, { key: "text", pre: true })
    expect(screen.getByTestId("pre-wrapped")).toBeInTheDocument()
})
