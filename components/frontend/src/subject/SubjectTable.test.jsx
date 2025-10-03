import { LocalizationProvider } from "@mui/x-date-pickers"
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs"
import { act, fireEvent, render, renderHook, screen } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings } from "../__fixtures__/fixtures"
import * as fetchServerApi from "../api/fetch_server_api"
import { useExpandedItemsSearchQuery } from "../app_ui_settings"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import {
    asyncClickButton,
    asyncClickRole,
    clickButton,
    expectFetch,
    expectNoAccessibilityViolations,
    expectNoText,
    expectText,
} from "../testUtils"
import { SubjectTable } from "./SubjectTable"

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

const dates = [
    new Date("2020-01-15T00:00:00+00:00"),
    new Date("2020-01-14T00:00:00+00:00"),
    new Date("2020-01-13T00:00:00+00:00"),
]

function renderSubjectTable({ dates = [], expandedItems = null, settings = null } = {}) {
    settings = settings ?? createTestableSettings()
    if (expandedItems) {
        settings.expandedItems = expandedItems
    }
    return render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={dataModel}>
                <LocalizationProvider dateAdapter={AdapterDayjs}>
                    <SubjectTable
                        dates={dates}
                        handleSort={vi.fn()}
                        reportDate={new Date("2020-01-15T00:00:00+00:00")}
                        report={{
                            report_uuid: "report_uuid",
                            subjects: {
                                subject_uuid: {
                                    type: "subject_type",
                                    metrics: { 1: metric, 2: metric2 },
                                },
                            },
                        }}
                        measurements={[
                            {
                                metric_uuid: "1",
                                start: "2020-01-14T00:00:00+00:00",
                                end: "2020-01-15T00:00:00+00:00",
                                count: { status: "target_met" },
                            },
                            {
                                metric_uuid: "1",
                                start: "2020-01-15T00:00:00+00:00",
                                end: "2020-01-16T00:00:00+00:00",
                                count: { status: "target_met" },
                            },
                            {
                                metric_uuid: "1",
                                start: "2020-01-16T00:00:00+00:00",
                                end: "2020-01-17T00:00:00+00:00",
                                count: { status: "target_not_met" },
                            },
                            {
                                metric_uuid: "2",
                                start: "2020-01-10T00:00:00+00:00",
                                end: "2020-01-10T00:00:00+00:00",
                                count: { status: "target_not_met" },
                            },
                            {
                                metric_uuid: "3",
                                start: "2020-01-14T00:00:00+00:00",
                                end: "2020-01-15T00:00:00+00:00",
                                count: { status: "target_not_met" },
                            },
                        ]}
                        metricEntries={Object.entries({ 1: metric, 2: metric2 })}
                        reports={[]}
                        settings={settings}
                        subject={{ type: "subject_type", metrics: { 1: metric, 2: metric2 } }}
                        subjectUuid="subject_uuid"
                    />
                </LocalizationProvider>
            </DataModel.Provider>
        </Permissions.Provider>,
    )
}

beforeEach(() => {
    history.push("")
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true })
})

it("displays all the metrics", async () => {
    const { container } = renderSubjectTable()
    const metricNames = ["name_1", "name_2"]
    metricNames.forEach((metricName) => {
        expectText(metricName)
    })
    await expectNoAccessibilityViolations(container)
})

it("shows the date columns", async () => {
    const { container } = renderSubjectTable({ dates: dates })
    dates.forEach((date) => {
        expectText(date.toLocaleDateString())
    })
    await expectNoAccessibilityViolations(container)
})

it("shows the source column", () => {
    renderSubjectTable()
    expectText(/Source/)
})

it("hides the source column", () => {
    history.push("?hidden_columns=source")
    renderSubjectTable()
    expectNoText(/Source/)
})

it("shows the time left column", () => {
    renderSubjectTable()
    expectText(/Time left/)
})

it("hides the time left column", () => {
    history.push("?hidden_columns=time_left")
    renderSubjectTable()
    expectNoText(/Time left/)
})

it("does not show the overrun column when showing one date", () => {
    renderSubjectTable()
    expectNoText(/[Oo]verrun/)
})

it("shows the overrun column when showing multiple dates", () => {
    renderSubjectTable({ dates: dates })
    expectText(/[Oo]verrun/)
})

it("hides the overrun column when showing multiple dates", () => {
    history.push("?hidden_columns=overrun")
    renderSubjectTable()
    expectNoText(/[Oo]verrun/)
})

it("shows the comment column", () => {
    renderSubjectTable()
    expectText(/Comment/)
})

it("hides the comment column", () => {
    history.push("?hidden_columns=comment")
    renderSubjectTable()
    expectNoText(/Comment/)
})

it("shows the issue column", () => {
    renderSubjectTable()
    expectText(/Issues/)
})

it("hides the issue column", () => {
    history.push("?hidden_columns=issues")
    renderSubjectTable()
    expectNoText(/Issues/)
})

it("shows the tags column", () => {
    renderSubjectTable()
    expectText(/Tags/)
    expectText(/Tag 1/)
})

it("hides the tags column", () => {
    history.push("?hidden_columns=tags")
    renderSubjectTable()
    expectNoText(/Tags/)
    expectNoText(/Tag 1/)
})

it("expands the details via the button", async () => {
    const expandedItems = renderHook(() => useExpandedItemsSearchQuery())
    const { container } = renderSubjectTable({ expandedItems: expandedItems.result.current })
    clickButton("Expand/collapse", 0)
    expandedItems.rerender()
    await expectNoAccessibilityViolations(container)
    expect(expandedItems.result.current.value).toStrictEqual(["1:0"])
})

it("collapses the details via the button", async () => {
    history.push("?expanded=1:0")
    const expandedItems = renderHook(() => useExpandedItemsSearchQuery())
    renderSubjectTable({ expandedItems: expandedItems.result.current })
    await asyncClickButton("Expand/collapse", 0)
    expandedItems.rerender()
    expect(expandedItems.result.current.value).toStrictEqual([])
})

it("expands the details via the url", async () => {
    history.push("?expanded=1:0")
    const { container } = renderSubjectTable()
    await act(async () => {}) // Wait for hooks to finish
    expectText("Configuration")
    await expectNoAccessibilityViolations(container)
})

it("moves a metric", async () => {
    history.push("?expanded=1:2")
    renderSubjectTable()
    await asyncClickButton("Move metric to the next row")
    expectFetch("post", "metric/1/attribute/position", { position: "next" })
})

it("adds a source", async () => {
    history.push("?expanded=1:1")
    const { container } = renderSubjectTable()
    await asyncClickRole("tab", /Sources/)
    const addButton = await screen.findByText("Add source")
    await act(async () => fireEvent.click(addButton))
    await expectNoAccessibilityViolations(container)
    fireEvent.click(await screen.findByText("Source type"))
    expectFetch("post", "source/new/1", { type: "source_type" })
})

it("hides empty columns", async () => {
    history.push("?hide_empty_columns=true")
    renderSubjectTable()
    expectNoText(/Comment/)
    expectNoText(/Issues/)
    expectText(/Tags/) // Not empty
})
