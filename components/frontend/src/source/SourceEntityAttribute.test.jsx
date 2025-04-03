import { render, screen } from "@testing-library/react"

import { expectNoAccessibilityViolations } from "../testUtils"
import { SourceEntityAttribute } from "./SourceEntityAttribute"

function renderSourceEntityAttribute(entity, entityAttribute) {
    return render(<SourceEntityAttribute entity={entity} entityAttribute={entityAttribute} />)
}

it("renders a string", async () => {
    const { container } = renderSourceEntityAttribute({ text: "some text" }, { key: "text" })
    expect(screen.queryAllByText(/some text/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders an empty string", async () => {
    const { container } = renderSourceEntityAttribute({ other: "will not be shown" }, { key: "missing" })
    expect(screen.queryAllByText(/will not be shown/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("renders a float", async () => {
    const { container } = renderSourceEntityAttribute({ number: 42.0 }, { key: "number", type: "float" })
    expect(screen.getAllByText(/42/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders a zero float", async () => {
    const { container } = renderSourceEntityAttribute({ number: 0.0 }, { key: "number", type: "float" })
    expect(screen.getAllByText(/0/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders an integer", async () => {
    const { container } = renderSourceEntityAttribute({ number: 42.0 }, { key: "number", type: "integer" })
    expect(screen.getAllByText(/42/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders an integer percentage", async () => {
    const { container } = renderSourceEntityAttribute({ number: 42.0 }, { key: "number", type: "integer_percentage" })
    expect(screen.getAllByText(/42%/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders a datetime", async () => {
    const { container } = renderSourceEntityAttribute(
        { timestamp: "2021-10-10T10:10:10" },
        { key: "timestamp", type: "datetime" },
    )
    expect(screen.getAllByText(/ago/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders a date", async () => {
    const { container } = renderSourceEntityAttribute({ date: "2021-10-10T10:10:10" }, { key: "date", type: "date" })
    expect(screen.getAllByText(/ago/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders minutes", async () => {
    const { container } = renderSourceEntityAttribute({ duration: "42" }, { key: "duration", type: "minutes" })
    expect(screen.getAllByText(/42/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders a status icon", async () => {
    const { container } = renderSourceEntityAttribute({ status: "target_met" }, { key: "status", type: "status" })
    expect(screen.getAllByLabelText("Target met").length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders a url", async () => {
    const { container } = renderSourceEntityAttribute(
        { status: "target_met", url: "https://url" },
        { key: "status", type: "status", url: "url" },
    )
    expect(screen.getByLabelText("Target met").closest("a").href).toBe("https://url/")
    await expectNoAccessibilityViolations(container)
})

it("renders preformatted text", async () => {
    const { container } = renderSourceEntityAttribute({ text: "text" }, { key: "text", pre: true })
    expect(screen.getByTestId("pre-wrapped")).toBeInTheDocument()
    await expectNoAccessibilityViolations(container)
})

it("renders a boolean that is true", async () => {
    const { container } = renderSourceEntityAttribute({ boolean: "true" }, { key: "boolean", type: "boolean" })
    expect(screen.queryAllByText(/✅/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders a boolean that is false", async () => {
    const { container } = renderSourceEntityAttribute({ boolean: "false" }, { key: "boolean", type: "boolean" })
    expect(screen.queryAllByText(/✅/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})
