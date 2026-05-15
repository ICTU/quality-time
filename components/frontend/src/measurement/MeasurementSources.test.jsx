import { render } from "@testing-library/react"

import { DataModelContext } from "../context/DataModel"
import { expectNoAccessibilityViolations, expectNoText, expectText } from "../testUtils"
import { MeasurementSources } from "./MeasurementSources"

const dataModel = {
    metrics: { metric_type: { sources: ["source_type"] } },
    sources: { source_type: { parameters: {} } },
}

const dataModelWithIdentifying = {
    metrics: { metric_type: { sources: ["source_type"] } },
    sources: {
        source_type: {
            identifying_parameters: ["date"],
            parameters: { date: { type: "date" } },
        },
    },
}

function renderMeasurementSources(sources, latestMeasurement, customDataModel = dataModel) {
    return render(
        <DataModelContext value={customDataModel}>
            <MeasurementSources
                metric={{
                    type: "metric_type",
                    sources: sources,
                    latest_measurement: latestMeasurement,
                }}
            />
        </DataModelContext>,
    )
}

it("has no accessibility violations", async () => {
    const { container } = renderMeasurementSources(
        { source_uuid: { type: "source_type", name: "Source name" } },
        { sources: [{ source_uuid: "source_uuid" }] },
    )
    await expectNoAccessibilityViolations(container)
})

it("renders one measurement source", async () => {
    renderMeasurementSources(
        { source_uuid: { type: "source_type", name: "Source name" } },
        { sources: [{ source_uuid: "source_uuid" }] },
    )
    expectText(/Source name/)
})

it("renders multiple measurement sources", async () => {
    renderMeasurementSources(
        {
            source_uuid1: { type: "source_type", name: "Source name 1" },
            source_uuid2: { type: "source_type", name: "Source name 2" },
        },
        {
            sources: [{ source_uuid: "source_uuid1" }, { source_uuid: "source_uuid2" }],
        },
    )
    expectText(/Source name 1, Source name 2/)
})

it("uses a whitespace separator instead of a comma when any source has identifying values", async () => {
    renderMeasurementSources(
        {
            source_uuid1: {
                type: "source_type",
                name: "Source name 1",
                parameters: { date: "2026-06-01" },
            },
            source_uuid2: { type: "source_type", name: "Source name 2" },
        },
        {
            sources: [{ source_uuid: "source_uuid1" }, { source_uuid: "source_uuid2" }],
        },
        dataModelWithIdentifying,
    )
    expectText(/Source name 1/)
    expectText(/Source name 2/)
    expectNoText(/Source name 1, Source name 2/)
})
