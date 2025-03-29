import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { DataModel } from "../context/DataModel"
import { expectNoAccessibilityViolations } from "../testUtils"
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
    expect(screen.getAllByText(/Source name/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders the source label and the popup if there is an connection error", async () => {
    const { container } = renderSourceStatus(metric, { source_uuid: "source_uuid", connection_error: "error" })
    expect(screen.getAllByText(/Source name/).length).toBe(1)
    await userEvent.hover(screen.queryByText(/Source name/))
    await waitFor(async () => {
        expect(screen.queryByText("Connection error")).not.toBe(null)
        await expectNoAccessibilityViolations(container)
    })
})

it("renders the source label and the popup if there is a parse error", async () => {
    const { container } = renderSourceStatus(metric, { source_uuid: "source_uuid", parse_error: "error" })
    expect(screen.getAllByText(/Source name/).length).toBe(1)
    await userEvent.hover(screen.queryByText(/Source name/))
    await waitFor(async () => {
        expect(screen.queryByText("Parse error")).not.toBe(null)
        await expectNoAccessibilityViolations(container)
    })
})

it("renders the source label and the popup if there is a configuration error", async () => {
    metric.sources["source_uuid"]["type"] = "source_type2"
    const { container } = renderSourceStatus(metric, { source_uuid: "source_uuid" })
    expect(screen.getAllByText(/Source name/).length).toBe(1)
    await userEvent.hover(screen.queryByText(/Source name/))
    await waitFor(async () => {
        expect(screen.queryByText("Configuration error")).not.toBe(null)
        await expectNoAccessibilityViolations(container)
    })
})

it("renders nothing if the source has been deleted", async () => {
    const { container } = renderSourceStatus(metric, { source_uuid: "other_source_uuid" })
    expect(screen.queryByText(/Source name/)).toBe(null)
    await expectNoAccessibilityViolations(container)
})
