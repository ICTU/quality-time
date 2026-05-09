import { render, screen } from "@testing-library/react"

import { dataModel } from "../__fixtures__/fixtures"
import { DataModelContext } from "../context/DataModel"
import { expectText } from "../testUtils"
import { UnusedMetricTypes } from "./UnusedMetricTypes"

function renderUnusedMetricTypes(theReport, source) {
    return render(
        <DataModelContext value={dataModel}>
            <UnusedMetricTypes report={theReport} source={source} />
        </DataModelContext>,
    )
}

it("shows the unused metric types", async () => {
    const report = {
        subjects: {
            subject_uuid: {
                metrics: {
                    metric_uuid: {
                        type: "metric_type",
                        sources: {
                            source_uuid: {
                                type: "source_type",
                                parameters: { url: "https://example.org" },
                            },
                        },
                    },
                    metric_uuid2: {
                        type: "metric_type",
                        sources: {
                            source_uuid2: {
                                type: "source_type_without_location_parameters",
                                parameters: { url: "https://example.org" },
                            },
                        },
                    },
                },
            },
        },
    }
    renderUnusedMetricTypes(report, { type: "source_type_without_location_parameters", parameters: {} })
    expectText("Metric type 2")
    const readTheDocsLink = screen.getByRole("link", { name: "Metric type 2" })
    expect(readTheDocsLink).toHaveAttribute("href", expect.stringContaining("#metric-type-2"))
    expectText("Metric type description")
    expectText("Metric type rationale")
})

it("shows a message if there are no unused metric types", async () => {
    const report = {
        subjects: {
            subject_uuid: {
                metrics: {
                    metric_uuid: {
                        type: "metric_type",
                        sources: {
                            source_uuid: {
                                type: "source_type",
                                parameters: { url: "https://example.org" },
                            },
                        },
                    },
                },
            },
        },
    }
    renderUnusedMetricTypes(report, { type: "source_type", parameters: { url: "https://example.org" } })
    expectText("All metric types that this source supports are being used.")
})
