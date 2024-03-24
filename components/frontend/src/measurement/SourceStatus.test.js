import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { DataModel } from "../context/DataModel"
import { SourceStatus } from "./SourceStatus"

const metric = {
    type: "metric_type",
    sources: { source_uuid: { type: "source_type", name: "Source name" } },
}
const dataModel = { metrics: { metric_type: { sources: ["source_type"] } } }

function renderSourceStatus(metric, measurement_source) {
    return render(
        <DataModel.Provider value={dataModel}>
            <SourceStatus metric={metric} measurement_source={measurement_source} />
        </DataModel.Provider>,
    )
}

it("renders the hyperlink label if the source has a landing url", () => {
    renderSourceStatus(metric, { landing_url: "https://landing", source_uuid: "source_uuid" })
    expect(screen.getAllByRole("link").length).toBe(1)
})

it("renders the source label if there is no error", () => {
    renderSourceStatus(metric, { source_uuid: "source_uuid" })
    expect(screen.getAllByText(/Source name/).length).toBe(1)
})

it("renders the source label and the popup if there is an connection error", async () => {
    renderSourceStatus(metric, { source_uuid: "source_uuid", connection_error: "error" })
    expect(screen.getAllByText(/Source name/).length).toBe(1)
    await userEvent.hover(screen.queryByText(/Source name/))
    await waitFor(() => {
        expect(screen.queryByText("Connection error")).not.toBe(null)
    })
})

it("renders the source label and the popup if there is a parse error", async () => {
    renderSourceStatus(metric, { source_uuid: "source_uuid", parse_error: "error" })
    expect(screen.getAllByText(/Source name/).length).toBe(1)
    await userEvent.hover(screen.queryByText(/Source name/))
    await waitFor(() => {
        expect(screen.queryByText("Parse error")).not.toBe(null)
    })
})

it("renders the source label and the popup if there is a configuration error", async () => {
    metric.sources["source_uuid"]["type"] = "source_type2"
    renderSourceStatus(metric, { source_uuid: "source_uuid" })
    expect(screen.getAllByText(/Source name/).length).toBe(1)
    await userEvent.hover(screen.queryByText(/Source name/))
    await waitFor(() => {
        expect(screen.queryByText("Configuration error")).not.toBe(null)
    })
})

it("renders nothing if the source has been deleted", () => {
    renderSourceStatus(metric, { source_uuid: "other_source_uuid" })
    expect(screen.queryByText(/Source name/)).toBe(null)
})
