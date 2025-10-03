import { render, screen } from "@testing-library/react"

import { DataModel } from "../context/DataModel"
import { expectNoAccessibilityViolations, expectNoText, expectText, expectTextAfterWait, hoverText } from "../testUtils"
import { SourceStatus } from "./SourceStatus"

const metric = {
    type: "metric_type",
    sources: { source_uuid: { type: "source_type", name: "Source name" } },
}
const dataModel = { metrics: { metric_type: { sources: ["source_type"] } } }

function renderSourceStatus(metric, measurementSource) {
    return render(
        <DataModel.Provider value={dataModel}>
            <SourceStatus metric={metric} measurementSource={measurementSource} />
        </DataModel.Provider>,
    )
}

it("renders the hyperlink label if the source has a landing url", async () => {
    const { container } = renderSourceStatus(metric, { landing_url: "https://landing", source_uuid: "source_uuid" })
    expect(screen.getAllByRole("link").length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders the source label if there is no error", async () => {
    const { container } = renderSourceStatus(metric, { source_uuid: "source_uuid" })
    expectText(/Source name/)
    await expectNoAccessibilityViolations(container)
})

it("renders the source label and the popup if there is an connection error", async () => {
    const { container } = renderSourceStatus(metric, { source_uuid: "source_uuid", connection_error: "error" })
    expectText(/Source name/)
    await hoverText(/Source name/)
    await expectTextAfterWait("Connection error")
    await expectNoAccessibilityViolations(container)
})

it("renders the source label and the popup if there is a parse error", async () => {
    const { container } = renderSourceStatus(metric, { source_uuid: "source_uuid", parse_error: "error" })
    expectText(/Source name/)
    await hoverText(/Source name/)
    await expectTextAfterWait("Parse error")
    await expectNoAccessibilityViolations(container)
})

it("renders the source label and the popup if there is a configuration error", async () => {
    metric.sources["source_uuid"]["type"] = "source_type2"
    const { container } = renderSourceStatus(metric, { source_uuid: "source_uuid" })
    expectText(/Source name/)
    await hoverText(/Source name/)
    await expectTextAfterWait("Configuration error")
    await expectNoAccessibilityViolations(container)
})

it("renders nothing if the source has been deleted", async () => {
    const { container } = renderSourceStatus(metric, { source_uuid: "other_source_uuid" })
    expectNoText(/Source name/)
    await expectNoAccessibilityViolations(container)
})
