import { render, screen } from "@testing-library/react"

import { dataModel } from "../__fixtures__/fixtures"
import { DataModelContext } from "../context/DataModel"
import { expectNoAccessibilityViolations, expectText } from "../testUtils"
import { UnusedMetricTypes } from "./UnusedMetricTypes"

function renderUnusedMetricTypes(report, sourceLocationUuid) {
    return render(
        <DataModelContext value={dataModel}>
            <UnusedMetricTypes report={report} sourceLocationUuid={sourceLocationUuid} />
        </DataModelContext>,
    )
}

it("shows the unused metric types", async () => {
    const report = {
        source_locations: {
            source_location_uuid: { source_type: "source_type_without_location_parameters" },
        },
        subjects: {
            subject_uuid: {
                metrics: {
                    metric_uuid: {
                        type: "metric_type",
                        sources: {
                            source_uuid: {
                                type: "source_type_without_location_parameters",
                                source_location: "source_location_uuid",
                            },
                        },
                    },
                },
            },
        },
    }
    const { container } = renderUnusedMetricTypes(report, "source_location_uuid")
    expectText("Metric type 2")
    const readTheDocsLink = screen.getByRole("link", { name: "Metric type 2" })
    expect(readTheDocsLink).toHaveAttribute("href", expect.stringContaining("#metric-type-2"))
    expectText("Metric type description")
    expectText("Metric type rationale")
    await expectNoAccessibilityViolations(container)
})

it("shows a message if there are no unused metric types", async () => {
    const report = {
        source_locations: {
            source_location_uuid: { source_type: "source_type" },
        },
        subjects: {
            subject_uuid: {
                metrics: {
                    metric_uuid: {
                        type: "metric_type",
                        sources: {
                            source_uuid: {
                                type: "source_type",
                                source_location: "source_location_uuid",
                            },
                        },
                    },
                },
            },
        },
    }
    const { container } = renderUnusedMetricTypes(report, "source_location_uuid")
    expectText("All metric types that this source location supports are being used.")
    await expectNoAccessibilityViolations(container)
})
