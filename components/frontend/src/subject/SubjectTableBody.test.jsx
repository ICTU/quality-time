import { createEvent, fireEvent, render, screen } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings, dataModel, report } from "../__fixtures__/fixtures"
import { setMetricAttribute } from "../api/metric"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectNoAccessibilityViolations } from "../testUtils"
import { SubjectTableBody } from "./SubjectTableBody"

vi.mock("../utils", async () => {
    const actual = await vi.importActual("../utils")
    return {
        ...actual,
        createDragGhost: vi.fn(),
    }
})

vi.mock("../api/metric", async () => {
    const actual = await vi.importActual("../api/metric")
    return {
        ...actual,
        setMetricAttribute: vi.fn().mockResolvedValue({}),
    }
})

function renderSubjectTableBody({ dates = [], expandedItems = null, settings = null } = {}) {
    settings = settings ?? createTestableSettings()
    if (expandedItems) {
        settings.expandedItems = expandedItems
    }
    return render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={dataModel}>
                <table>
                    <SubjectTableBody
                        columnsToHide={[]}
                        dates={dates}
                        handleSort={vi.fn()}
                        measurements={[]}
                        metricEntries={Object.entries({
                            1: report.subjects.subject_uuid.metrics.metric_uuid,
                            2: report.subjects.subject_uuid.metrics.metric_uuid2,
                        })}
                        reload={vi.fn()}
                        report={report}
                        reportDate={new Date("2020-01-15T00:00:00+00:00")}
                        reports={[]}
                        reversedMeasurements={[]}
                        settings={settings}
                        subject_uuid="subject_uuid"
                        tags={[]}
                    />
                </table>
            </DataModel.Provider>
        </Permissions.Provider>,
    )
}

function simulateDragAndDrop() {
    renderSubjectTableBody()

    const row0 = screen.getByTestId("metric-row-0")
    const row1 = screen.getByTestId("metric-row-1")

    // Simulate drag start on the first row
    const dragStartEvent = createEvent.dragStart(row0)
    dragStartEvent.dataTransfer = { effectAllowed: "", setDragImage: vi.fn() }
    fireEvent(row0, dragStartEvent)

    // Simulate drag enter on the second row
    fireEvent.dragEnter(row1)

    // Simulate drop on the second row
    const dropEvent = createEvent.drop(row1)
    dropEvent.preventDefault = vi.fn()
    fireEvent(row1, dropEvent)
}

beforeEach(() => {
    history.push("")
    setMetricAttribute.mockClear()
})

it("shows the correct number of rows", async () => {
    const { container } = renderSubjectTableBody()
    expect(screen.queryAllByTestId(/^metric-row-/).length).toBe(2)
    await expectNoAccessibilityViolations(container)
})

it("shows drop indicator when dragging over a row", () => {
    renderSubjectTableBody()
    // Simulate drag enter on the 2nd row
    const row = screen.getByTestId("metric-row-1")
    fireEvent.dragEnter(row)
    expect(screen.getByTestId("drop-indicator-1")).toBeInTheDocument()
})

it("sets up drag start correctly", () => {
    renderSubjectTableBody()
    const row = screen.getByTestId("metric-row-0")
    const dragStartEvent = createEvent.dragStart(row)
    dragStartEvent.dataTransfer = {
        effectAllowed: "",
        setDragImage: vi.fn(),
    }

    fireEvent(row, dragStartEvent)

    expect(dragStartEvent.dataTransfer.effectAllowed).toBe("move")
})

it("handles drag end by resetting drag state", async () => {
    renderSubjectTableBody({})

    const row0 = screen.getByTestId("metric-row-0")
    const row1 = screen.getByTestId("metric-row-1")

    const dragStartEvent = createEvent.dragStart(row0)
    dragStartEvent.dataTransfer = {
        effectAllowed: "",
        setDragImage: vi.fn(), // needed if `createDragGhost` sets it
    }
    fireEvent(row0, dragStartEvent)

    fireEvent.dragEnter(row1)

    const dropEvent = createEvent.drop(row1)
    dropEvent.preventDefault = vi.fn()
    fireEvent(row1, dropEvent)

    // Drop indicator should no longer be visible
    expect(screen.queryByTestId("drop-indicator-1")).not.toBeInTheDocument()
})

it("handles drop by reordering metrics", () => {
    simulateDragAndDrop()

    // Check API call
    expect(setMetricAttribute).toHaveBeenCalledWith("1", "position_index", 1, expect.any(Function))

    // Check reorder by verifying row contents
    const rows = screen.getAllByTestId(/metric-row-/)

    const firstRowText = rows[0].textContent
    const secondRowText = rows[1].textContent

    expect(firstRowText).toContain("M2")
    expect(secondRowText).toContain("M1")
})

it("does not reorder metrics if drop target is the same as drag source", () => {
    renderSubjectTableBody()

    const row0 = screen.getByTestId("metric-row-0")

    // Simulate drag start on the first row
    const dragStartEvent = createEvent.dragStart(row0)
    dragStartEvent.dataTransfer = { effectAllowed: "", setDragImage: vi.fn() }
    fireEvent(row0, dragStartEvent)

    // Simulate dragging over the same row
    fireEvent.dragEnter(row0)

    // Simulate drop on the same row

    const dropEvent = createEvent.drop(row0)
    dropEvent.preventDefault = vi.fn()
    fireEvent(row0, dropEvent)

    // Verify no API call was made
    expect(setMetricAttribute).not.toHaveBeenCalled()
})

it("Shows a console log if API call fails", async () => {
    // Mock setMetricAttribute to reject
    setMetricAttribute.mockRejectedValueOnce(new Error("API error"))
    const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {})

    simulateDragAndDrop()

    // Wait for the promise to settle
    await Promise.resolve()

    expect(consoleErrorSpy).toHaveBeenCalledWith("Failed to update metric position:", expect.any(Error))
    consoleErrorSpy.mockRestore()
})

it("resets drag state on dragend", () => {
    renderSubjectTableBody()

    const row1 = screen.getByTestId("metric-row-1")
    fireEvent.dragEnter(row1)
    expect(screen.getByTestId("drop-indicator-1")).toBeInTheDocument()

    // Simulate dragend on window
    fireEvent(window, new Event("dragend"))

    // Drop indicator should be gone
    expect(screen.queryByTestId("drop-indicator-1")).not.toBeInTheDocument()
})
