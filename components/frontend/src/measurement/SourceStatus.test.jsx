import { render, screen } from "@testing-library/react"

import { DataModelContext } from "../context/DataModel"
import { expectNoAccessibilityViolations, expectNoText, expectText, expectTextAfterWait, hoverText } from "../testUtils"
import { SourceStatus } from "./SourceStatus"

const dataModel = {
    metrics: { metric_type: { sources: ["source_type"] } },
    sources: { source_type: { name: "Source type name" } },
}

function metric(source_type = "source_type") {
    return {
        type: "metric_type",
        sources: { source_uuid: { type: source_type, name: "Source name" } },
    }
}

function renderSourceStatus(metric, measurementSource, report) {
    return render(
        <DataModelContext value={dataModel}>
            <SourceStatus metric={metric} measurementSource={measurementSource} report={report} />
        </DataModelContext>,
    )
}

it("has no accessibility violations", async () => {
    const { container } = renderSourceStatus(metric(), { landing_url: "https://landing", source_uuid: "source_uuid" })
    await expectNoAccessibilityViolations(container)
})

it("renders the hyperlink label if the source has a landing url", async () => {
    renderSourceStatus(metric(), { landing_url: "https://landing", source_uuid: "source_uuid" })
    expect(screen.getAllByRole("link").length).toBe(1)
})

it("renders the source label if there is no error", async () => {
    renderSourceStatus(metric(), { source_uuid: "source_uuid" })
    expectText(/Source name/)
})

it("renders the source label and the popup if there is an connection error", async () => {
    renderSourceStatus(metric(), { source_uuid: "source_uuid", connection_error: "error" })
    expectText(/Source name/)
    await hoverText(/Source name/)
    await expectTextAfterWait("Connection error")
})

it("renders the source label and the popup if there is a parse error", async () => {
    renderSourceStatus(metric(), { source_uuid: "source_uuid", parse_error: "error" })
    expectText(/Source name/)
    await hoverText(/Source name/)
    await expectTextAfterWait("Parse error")
})

it("renders the source label and the popup if there is a configuration error", async () => {
    renderSourceStatus(metric("source_type2"), { source_uuid: "source_uuid" })
    expectText(/Source name/)
    await hoverText(/Source name/)
    await expectTextAfterWait("Configuration error")
})

it("renders the source label and the popup if there is an info message", async () => {
    renderSourceStatus(metric(), { source_uuid: "source_uuid", info_message: "Some info" })
    expectText(/Source name/)
    await hoverText(/Source name/)
    await expectTextAfterWait("Note")
})

it("renders nothing if the source has been deleted", async () => {
    renderSourceStatus(metric(), { source_uuid: "other_source_uuid" })
    expectNoText(/Source name/)
})

it("renders the source location name if the source has no name but its source location does", async () => {
    const metricWithUnnamedSource = {
        type: "metric_type",
        sources: { source_uuid: { type: "source_type", source_location: "source_location_uuid" } },
    }
    const report = { source_locations: { source_location_uuid: { location_name: "Source location name" } } }
    renderSourceStatus(metricWithUnnamedSource, { source_uuid: "source_uuid" }, report)
    expectText(/Source location name/)
})

it("renders the source type name if neither the source nor its source location has a name", async () => {
    const metricWithUnnamedSource = {
        type: "metric_type",
        sources: { source_uuid: { type: "source_type", source_location: "source_location_uuid" } },
    }
    const report = { source_locations: { source_location_uuid: {} } }
    renderSourceStatus(metricWithUnnamedSource, { source_uuid: "source_uuid" }, report)
    expectText(/Source type name/)
})
