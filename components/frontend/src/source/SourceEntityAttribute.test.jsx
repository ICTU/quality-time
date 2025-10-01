import { render, screen } from "@testing-library/react"

import { expectLabelText, expectNoAccessibilityViolations, expectNoText, expectText } from "../testUtils"
import { SourceEntityAttribute } from "./SourceEntityAttribute"

function renderSourceEntityAttribute(entity, entityAttribute) {
    return render(<SourceEntityAttribute entity={entity} entityAttribute={entityAttribute} />)
}

it("renders a string", async () => {
    const { container } = renderSourceEntityAttribute({ text: "some text" }, { key: "text" })
    expectText(/some text/)
    await expectNoAccessibilityViolations(container)
})

it("renders an empty string", async () => {
    const { container } = renderSourceEntityAttribute({ other: "will not be shown" }, { key: "missing" })
    expectNoText(/will not be shown/)
    await expectNoAccessibilityViolations(container)
})

it("renders a float", async () => {
    const { container } = renderSourceEntityAttribute({ number: 42.0 }, { key: "number", type: "float" })
    expectText(/42/)
    await expectNoAccessibilityViolations(container)
})

it("renders a zero float", async () => {
    const { container } = renderSourceEntityAttribute({ number: 0.0 }, { key: "number", type: "float" })
    expectText(/0/)
    await expectNoAccessibilityViolations(container)
})

it("renders an integer", async () => {
    const { container } = renderSourceEntityAttribute({ number: 42.0 }, { key: "number", type: "integer" })
    expectText(/42/)
    await expectNoAccessibilityViolations(container)
})

it("renders an integer percentage", async () => {
    const { container } = renderSourceEntityAttribute({ number: 42.0 }, { key: "number", type: "integer_percentage" })
    expectText(/42%/)
    await expectNoAccessibilityViolations(container)
})

it("renders a datetime", async () => {
    const { container } = renderSourceEntityAttribute(
        { timestamp: "2021-10-10T10:10:10" },
        { key: "timestamp", type: "datetime" },
    )
    expectText(/ago/)
    await expectNoAccessibilityViolations(container)
})

it("renders a date", async () => {
    const { container } = renderSourceEntityAttribute({ date: "2021-10-10T10:10:10" }, { key: "date", type: "date" })
    expectText(/ago/)
    await expectNoAccessibilityViolations(container)
})

it("renders minutes", async () => {
    const { container } = renderSourceEntityAttribute({ duration: "42" }, { key: "duration", type: "minutes" })
    expectText(/42/)
    await expectNoAccessibilityViolations(container)
})

it("renders a status icon", async () => {
    const { container } = renderSourceEntityAttribute({ status: "target_met" }, { key: "status", type: "status" })
    expectLabelText("Target met")
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
    expectText(/✅/)
    await expectNoAccessibilityViolations(container)
})

it("renders a boolean that is false", async () => {
    const { container } = renderSourceEntityAttribute({ boolean: "false" }, { key: "boolean", type: "boolean" })
    expectNoText(/✅/)
    await expectNoAccessibilityViolations(container)
})
