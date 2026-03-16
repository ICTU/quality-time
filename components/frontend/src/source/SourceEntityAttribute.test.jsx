import { render, screen } from "@testing-library/react"

import { expectLabelText, expectNoAccessibilityViolations, expectNoText, expectText } from "../testUtils"
import { SourceEntityAttribute } from "./SourceEntityAttribute"

function renderSourceEntityAttribute(entity, entityAttribute) {
    return render(<SourceEntityAttribute entity={entity} entityAttribute={entityAttribute} />)
}

it("has no accessibility violations", async () => {
    const { container } = renderSourceEntityAttribute({ text: "some text" }, { key: "text" })
    await expectNoAccessibilityViolations(container)
})

it("renders a string", async () => {
    renderSourceEntityAttribute({ text: "some text" }, { key: "text" })
    expectText(/some text/)
})

it("renders an empty string", async () => {
    renderSourceEntityAttribute({ other: "will not be shown" }, { key: "missing" })
    expectNoText(/will not be shown/)
})

it("renders a float", async () => {
    renderSourceEntityAttribute({ number: 42.0 }, { key: "number", type: "float" })
    expectText(/42/)
})

it("renders a zero float", async () => {
    renderSourceEntityAttribute({ number: 0.0 }, { key: "number", type: "float" })
    expectText(/0/)
})

it("renders an integer", async () => {
    renderSourceEntityAttribute({ number: 42.0 }, { key: "number", type: "integer" })
    expectText(/42/)
})

it("renders an integer percentage", async () => {
    renderSourceEntityAttribute({ number: 42.0 }, { key: "number", type: "integer_percentage" })
    expectText(/42%/)
})

it("renders a datetime", async () => {
    renderSourceEntityAttribute({ timestamp: "2021-10-10T10:10:10" }, { key: "timestamp", type: "datetime" })
    expectText(/ago/)
})

it("renders a date", async () => {
    renderSourceEntityAttribute({ date: "2021-10-10T10:10:10" }, { key: "date", type: "date" })
    expectText(/ago/)
})

it("renders minutes", async () => {
    renderSourceEntityAttribute({ duration: "42" }, { key: "duration", type: "minutes" })
    expectText(/42/)
})

it("renders a status icon", async () => {
    renderSourceEntityAttribute({ status: "target_met" }, { key: "status", type: "status" })
    expectLabelText("Target met")
})

it("renders a url", async () => {
    renderSourceEntityAttribute(
        { status: "target_met", url: "https://url" },
        { key: "status", type: "status", url: "url" },
    )
    expect(screen.getByLabelText("Target met").closest("a").href).toBe("https://url/")
})

it("renders preformatted text", async () => {
    renderSourceEntityAttribute({ text: "text" }, { key: "text", pre: true })
    expect(screen.getByTestId("pre-wrapped")).toBeInTheDocument()
})

it("renders a boolean that is true", async () => {
    renderSourceEntityAttribute({ boolean: "true" }, { key: "boolean", type: "boolean" })
    expectText(/✅/)
})

it("renders a boolean that is false", async () => {
    renderSourceEntityAttribute({ boolean: "false" }, { key: "boolean", type: "boolean" })
    expectNoText(/✅/)
})
