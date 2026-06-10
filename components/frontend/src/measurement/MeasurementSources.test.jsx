import { render } from "@testing-library/react"

import { DataModelContext } from "../context/DataModel"
import { expectNoAccessibilityViolations, expectText } from "../testUtils"
import { MeasurementSources } from "./MeasurementSources"

const dataModel = { metrics: { metric_type: { sources: ["source_type"] } } }

function renderMeasurementSources(sources, latestMeasurement, report) {
    return render(
        <DataModelContext value={dataModel}>
            <MeasurementSources
                metric={{
                    type: "metric_type",
                    sources: sources,
                    latest_measurement: latestMeasurement,
                }}
                report={report}
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

it("renders the source location name if the source has no name", async () => {
    renderMeasurementSources(
        { source_uuid: { type: "source_type", source_location: "source_location_uuid" } },
        { sources: [{ source_uuid: "source_uuid" }] },
        { source_locations: { source_location_uuid: { location_name: "Source location name" } } },
    )
    expectText(/Source location name/)
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
