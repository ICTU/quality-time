import { Table, TableBody } from "@mui/material"
import { render } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings, dataModel, report } from "../__fixtures__/fixtures"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import {
    expectLabelText,
    expectNoAccessibilityViolations,
    expectNoLabelText,
    expectNoText,
    expectText,
} from "../testUtils"
import { SubjectTableRow } from "./SubjectTableRow"

beforeEach(() => history.push(""))

function renderSubjectTableRow({
    comment = "",
    direction = "<",
    ascending = false,
    scale = "count",
    evaluateTargets = undefined,
    expanded = false,
    permissions = "",
    name = "",
    secondaryName = "",
} = {}) {
    const dates = [new Date("2024-01-03"), new Date("2024-01-02"), new Date("2024-01-01")]
    const reverseMeasurements = [
        {
            metric_uuid: "metric_uuid",
            start: "2024-01-03T00:00",
            end: "2024-01-03T00:00",
            count: { value: "8", status: "target_met" },
            version_number: { value: "0.8", status: "target_met" },
        },
        {
            metric_uuid: "metric_uuid",
            start: "2024-01-02T00:00",
            end: "2024-01-02T00:00",
            count: { value: "12", status: "target_met" },
            version_number: { value: "1.2", status: "target_met" },
        },
        {
            metric_uuid: "metric_uuid",
            start: "2024-01-01T00:00",
            end: "2024-01-01T00:00",
            count: { value: "11", status: "target_met" },
            version_number: { value: "1.0", status: "target_met" },
        },
    ]
    if (ascending) {
        dates.reverse()
    }
    return render(
        <Permissions.Provider value={[permissions]}>
            <DataModel.Provider value={dataModel}>
                <Table>
                    <TableBody>
                        <SubjectTableRow
                            columnsToHide={[]}
                            dates={dates}
                            measurements={[]}
                            metric={{
                                comment: comment,
                                direction: direction,
                                evaluate_targets: evaluateTargets,
                                name: name,
                                recent_measurements: [],
                                scale: scale,
                                secondary_name: secondaryName,
                                type: "metric_type",
                                unit: "things",
                                unit_singular: "thing",
                            }}
                            metricUuid="metric_uuid"
                            report={report}
                            reversedMeasurements={reverseMeasurements}
                            settings={createTestableSettings({
                                expandedItems: {
                                    value: expanded ? ["metric_uuid:0"] : [],
                                    toggle: vi.fn(),
                                },
                                hiddenTags: { reset: vi.fn() },
                                metricsToHide: { reset: vi.fn() },
                            })}
                            subjectUuid="subject_uuid"
                        />
                    </TableBody>
                </Table>
            </DataModel.Provider>
        </Permissions.Provider>,
    )
}

it("shows the delta column", async () => {
    history.push("?nr_dates=3&date_interval=1")
    const { container } = renderSubjectTableRow()
    expectText("+1")
    expectLabelText("Metric type worsened from 11 to 12 things by +1 thing")
    expectText("-4")
    expectLabelText("Metric type improved from 12 to 8 things by -4 things")
    await expectNoAccessibilityViolations(container)
})

it("hides the delta column", async () => {
    history.push("?nr_dates=2&hidden_columns=delta")
    const { container } = renderSubjectTableRow()
    expectNoText("+1")
    expectNoText("-4")
    await expectNoAccessibilityViolations(container)
})

it("takes the metric direction into account", async () => {
    history.push("?nr_dates=3&date_interval=1")
    const { container } = renderSubjectTableRow({ direction: ">" })
    expectText("+1")
    expectLabelText("Metric type improved from 11 to 12 things by +1 thing")
    expectText("-4")
    expectLabelText("Metric type worsened from 12 to 8 things by -4 things")
    await expectNoAccessibilityViolations(container)
})

it("works for informative metrics", async () => {
    history.push("?nr_dates=3&date_interval=1")
    const { container } = renderSubjectTableRow({ evaluateTargets: false })
    expectText("+1")
    expectLabelText("Metric type changed from 11 to 12 things by +1 thing")
    expectText("-4")
    expectLabelText("Metric type changed from 12 to 8 things by -4 things")
    await expectNoAccessibilityViolations(container)
})

it("takes the date order into account", async () => {
    history.push("?nr_dates=3&date_interval=1&date_order=ascending")
    const { container } = renderSubjectTableRow({ ascending: true })
    expectText("+1")
    expectLabelText("Metric type worsened from 11 to 12 things by +1 thing")
    expectText("-4")
    expectLabelText("Metric type improved from 12 to 8 things by -4 things")
    await expectNoAccessibilityViolations(container)
})

it("shows the delta column for the version scale", async () => {
    history.push("?nr_dates=3&date_interval=1")
    const { container } = renderSubjectTableRow({ scale: "version_number" })
    expectText("+")
    expectLabelText("Metric type worsened from 1.0 to 1.2")
    expectText("-")
    expectLabelText("Metric type improved from 1.2 to 0.8")
    await expectNoAccessibilityViolations(container)
})

it("shows the drag handle when row is not expanded and user is authenticated", () => {
    renderSubjectTableRow({ permissions: EDIT_REPORT_PERMISSION })
    expectLabelText("Drag to reorder")
})

it("shows no drag handle when row is expanded", () => {
    renderSubjectTableRow({ expanded: true })
    expectNoLabelText("Drag to reorder")
})

it("shows no drag handle when rows are sorted", () => {
    // Simulate a sorted state by passing a non-empty sortColumn
    const settings = createTestableSettings()
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={dataModel}>
                <Table>
                    <TableBody>
                        <SubjectTableRow
                            columnsToHide={[]}
                            dates={[new Date("2024-01-03")]}
                            measurements={[]}
                            metric={report.subjects.subject_uuid.metrics.metric_uuid}
                            metricUuid="metric_uuid"
                            report={report}
                            reversedMeasurements={[]}
                            settings={{
                                ...settings,
                                // Ensure the settings object has a .sortColumn property with a .value
                                sortColumn: { value: "metric" },
                            }}
                            subjectUuid="subject_uuid"
                        />
                    </TableBody>
                </Table>
            </DataModel.Provider>
        </Permissions.Provider>,
    )
    expectNoLabelText("Drag to reorder")
})

it("shows the metric type as name if the metric has no name", async () => {
    const { container } = renderSubjectTableRow()
    expectText("Metric type")
    await expectNoAccessibilityViolations(container)
})

it("shows the metric name", async () => {
    const { container } = renderSubjectTableRow({ name: "Metric name" })
    expectText("Metric name")
    await expectNoAccessibilityViolations(container)
})

it("shows the metric secondary name", async () => {
    const { container } = renderSubjectTableRow({ secondaryName: "Secondary name" })
    expectText("Secondary name")
    await expectNoAccessibilityViolations(container)
})
