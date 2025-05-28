import { Table, TableBody } from "@mui/material"
import { render, screen } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings, dataModel, report } from "../__fixtures__/fixtures"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectNoAccessibilityViolations } from "../testUtils"
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
            count: { value: "10", status: "target_met" },
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
                                recent_measurements: [],
                                scale: scale,
                                type: "metric_type",
                                unit: "things",
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
    expect(screen.getAllByText("+2").length).toBe(1)
    expect(screen.getAllByLabelText("Metric type worsened from 10 to 12 things by +2 things").length).toBe(1)
    expect(screen.getAllByText("-4").length).toBe(1)
    expect(screen.getAllByLabelText("Metric type improved from 12 to 8 things by -4 things").length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("hides the delta column", async () => {
    history.push("?nr_dates=2&hidden_columns=delta")
    const { container } = renderSubjectTableRow()
    expect(screen.queryAllByText("+2").length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("takes the metric direction into account", async () => {
    history.push("?nr_dates=3&date_interval=1")
    const { container } = renderSubjectTableRow({ direction: ">" })
    expect(screen.getAllByText("+2").length).toBe(1)
    expect(screen.getAllByLabelText("Metric type improved from 10 to 12 things by +2 things").length).toBe(1)
    expect(screen.getAllByText("-4").length).toBe(1)
    expect(screen.getAllByLabelText("Metric type worsened from 12 to 8 things by -4 things").length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("works for informative metrics", async () => {
    history.push("?nr_dates=3&date_interval=1")
    const { container } = renderSubjectTableRow({ evaluateTargets: false })
    expect(screen.getAllByText("+2").length).toBe(1)
    expect(screen.getAllByLabelText("Metric type changed from 10 to 12 things by +2 things").length).toBe(1)
    expect(screen.getAllByText("-4").length).toBe(1)
    expect(screen.getAllByLabelText("Metric type changed from 12 to 8 things by -4 things").length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("takes the date order into account", async () => {
    history.push("?nr_dates=3&date_interval=1&date_order=ascending")
    const { container } = renderSubjectTableRow({ ascending: true })
    expect(screen.getAllByText("+2").length).toBe(1)
    expect(screen.getAllByLabelText("Metric type worsened from 10 to 12 things by +2 things").length).toBe(1)
    expect(screen.getAllByText("-4").length).toBe(1)
    expect(screen.getAllByLabelText("Metric type improved from 12 to 8 things by -4 things").length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows the delta column for the version scale", async () => {
    history.push("?nr_dates=3&date_interval=1")
    const { container } = renderSubjectTableRow({ scale: "version_number" })
    expect(screen.getAllByText("+").length).toBe(1)
    expect(screen.getAllByLabelText("Metric type worsened from 1.0 to 1.2").length).toBe(1)
    expect(screen.getAllByText("-").length).toBe(1)
    expect(screen.getAllByLabelText("Metric type improved from 1.2 to 0.8").length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows the drag handle when row is not expanded and user is authenticated", () => {
    renderSubjectTableRow({ permissions: EDIT_REPORT_PERMISSION })
    expect(screen.getByLabelText("Drag to reorder")).toBeInTheDocument()
})

it("shows no drag handle when row is expanded", () => {
    renderSubjectTableRow({ expanded: true })
    expect(screen.queryByLabelText("Drag to reorder")).not.toBeInTheDocument()
})
