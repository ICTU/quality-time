import { render, screen } from "@testing-library/react"

import { DataModelContext } from "../context/DataModel"
import { expectNoAccessibilityViolations, expectNoText, expectText, expectTextAfterWait, hoverText } from "../testUtils"
import { SourceStatus } from "./SourceStatus"

const dataModel = {
    metrics: { metric_type: { sources: ["source_type"] } },
    sources: { source_type: { parameters: {} } },
}

function dataModelWithIdentifying(parameterType = "date") {
    return {
        metrics: { metric_type: { sources: ["source_type"] } },
        sources: {
            source_type: {
                identifying_parameters: ["date"],
                parameters: { date: { type: parameterType } },
            },
        },
    }
}

function metric(source_type = "source_type", parameters = undefined) {
    return {
        type: "metric_type",
        sources: { source_uuid: { type: source_type, name: "Source name", parameters: parameters } },
    }
}

function renderSourceStatus(metric, measurementSource, customDataModel = dataModel) {
    return render(
        <DataModelContext value={customDataModel}>
            <SourceStatus metric={metric} measurementSource={measurementSource} />
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

it("renders the identifying parameter value below the source name", async () => {
    renderSourceStatus(
        metric("source_type", { date: "2026-06-01" }),
        { source_uuid: "source_uuid" },
        dataModelWithIdentifying(),
    )
    expectText(/Source name/)
    expectText(/Jun 1, 2026/)
})

it("does not render the identifying line when the parameter value is empty", async () => {
    renderSourceStatus(metric("source_type", { date: "" }), { source_uuid: "source_uuid" }, dataModelWithIdentifying())
    expectText(/Source name/)
    expectNoText(/Jun/)
})

it("renders the identifying parameter value next to the connection error label", async () => {
    renderSourceStatus(
        metric("source_type", { date: "2026-06-01" }),
        { source_uuid: "source_uuid", connection_error: "error" },
        dataModelWithIdentifying(),
    )
    expectText(/Source name/)
    expectText(/Jun 1, 2026/)
})
