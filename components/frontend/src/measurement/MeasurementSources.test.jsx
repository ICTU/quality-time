import { render } from "@testing-library/react"

import { DataModel } from "../context/DataModel"
import { expectNoAccessibilityViolations, expectText } from "../testUtils"
import { MeasurementSources } from "./MeasurementSources"

const dataModel = { metrics: { metric_type: { sources: ["source_type"] } } }

function renderMeasurementSources(sources, latestMeasurement) {
    return render(
        <DataModel.Provider value={dataModel}>
            <MeasurementSources
                metric={{
                    type: "metric_type",
                    sources: sources,
                    latest_measurement: latestMeasurement,
                }}
            />
        </DataModel.Provider>,
    )
}

it("renders one measurement source", async () => {
    const { container } = renderMeasurementSources(
        { source_uuid: { type: "source_type", name: "Source name" } },
        { sources: [{ source_uuid: "source_uuid" }] },
    )
    expectText(/Source name/)
    await expectNoAccessibilityViolations(container)
})

it("renders multiple measurement sources", async () => {
    const { container } = renderMeasurementSources(
        {
            source_uuid1: { type: "source_type", name: "Source name 1" },
            source_uuid2: { type: "source_type", name: "Source name 2" },
        },
        {
            sources: [{ source_uuid: "source_uuid1" }, { source_uuid: "source_uuid2" }],
        },
    )
    expectText(/Source name 1, Source name 2/)
    await expectNoAccessibilityViolations(container)
})
