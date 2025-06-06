import { createEvent, fireEvent, render, screen } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings } from "../__fixtures__/fixtures"
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

const metric = {
    unit: "testUnit",
    scale: "count",
    type: "metric_type",
    name: "name_1",
    sources: {},
    tags: ["Tag 1"],
}
const metric2 = {
    unit: "tests",
    scale: "percentage",
    name: "name_2",
    type: "metric_type",
}
const dataModel = {
    metrics: {
        metric_type: { name: "Metric type", sources: ["source_type"], tags: [] },
    },
    sources: {
        source_type: { name: "Source type" },
    },
    subjects: {
        subject_type: { metrics: ["metric_type"] },
    },
}

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
                        dates={dates}
                        handleSort={vi.fn()}
                        reportDate={new Date("2020-01-15T00:00:00+00:00")}
                        reload={vi.fn()}
                        reversedMeasurements={[]}
                        report={{
                            subjects: {
                                subject_uuid: {
                                    type: "subject_type",
                                    name: "Subject 1 title",
                                    metrics: {
                                        metric_uuid: {
                                            name: "M1",
                                            type: "metric_type",
                                            tags: ["other tag"],
                                            target: "1",
                                            sources: { source_uuid: { name: "Source" } },
                                            status: "target_not_met",
                                            recent_measurements: [],
                                            latest_measurement: { count: 1 },
                                            comment: "Comment 1",
                                        },
                                        metric_uuid2: {
                                            name: "M2",
                                            type: "metric_type",
                                            tags: ["tag"],
                                            target: "2",
                                            issue_ids: ["ABC-42"],
                                            sources: { source_uuid2: { name: "Source 2" } },
                                            status: "informative",
                                            recent_measurements: [],
                                            latest_measurement: { count: 2 },
                                            comment: "Comment 2",
                                        },
                                    },
                                },
                            },
                            title: "Report title",
                        }}
                        metricEntries={Object.entries({ 1: metric, 2: metric2 })}
                        reports={[]}
                        settings={settings}
                        subject_uuid="subject_uuid"
                        tags={[]}
                    />
                </table>
            </DataModel.Provider>
        </Permissions.Provider>,
    )
}

beforeEach(() => {
    history.push("")
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
    renderSubjectTableBody()

    const row0 = screen.getByTestId("metric-row-0")
    const row1 = screen.getByTestId("metric-row-1")

    const dragStartEvent = createEvent.dragStart(row0)
    dragStartEvent.dataTransfer = { effectAllowed: "", setDragImage: vi.fn() }
    fireEvent(row0, dragStartEvent)

    // Simulate drag enter to set drop index
    fireEvent.dragEnter(row1)

    const dropEvent = createEvent.drop(row1)
    dropEvent.preventDefault = vi.fn()
    fireEvent(row1, dropEvent)

    // Check API call
    expect(setMetricAttribute).toHaveBeenCalledWith("1", "position_index", 1)

    // Check reorder by verifying row contents
    const rows = screen.getAllByTestId(/metric-row-/)

    const firstRowText = rows[0].textContent
    const secondRowText = rows[1].textContent

    expect(firstRowText).toContain("name_2")
    expect(secondRowText).toContain("name_1")
})
