import { ThemeProvider } from "@mui/material/styles"
import { act, fireEvent, render, renderHook, screen } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings, dataModel } from "../__fixtures__/fixtures"
import * as fetch_server_api from "../api/fetch_server_api"
import { useHiddenTagsURLSearchQuery } from "../app_ui_settings"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { mockGetAnimations } from "../dashboard/MockAnimations"
import { expectNoAccessibilityViolations } from "../testUtils"
import { theme } from "../theme"
import { Report } from "./Report"

vi.mock("../api/fetch_server_api.js")

beforeEach(() => {
    fetch_server_api.fetch_server_api = vi.fn().mockReturnValue({ then: vi.fn().mockReturnValue({ finally: vi.fn() }) })
    mockGetAnimations()
    history.push("")
})

afterEach(() => vi.restoreAllMocks())

const report = {
    report_uuid: "report_uuid",
    title: "Report",
    subjects: {
        subject_uuid: {
            type: "subject_type",
            name: "Subject title",
            metrics: {
                metric_uuid: {
                    name: "Metric name",
                    type: "metric_type",
                    tags: ["tag"],
                    recent_measurements: [],
                },
                another_metric_uuid: {
                    name: "Metric name",
                    type: "metric_type",
                    tags: ["other"],
                    recent_measurements: [],
                },
            },
        },
    },
}

async function renderReport({
    reportToRender = null,
    dates = [new Date()],
    handleSort = vi.fn(),
    hiddenTags = null,
    report_date = null,
} = {}) {
    const settings = createTestableSettings()
    if (hiddenTags) {
        settings.hiddenTags = hiddenTags
    }
    let result
    await act(async () => {
        result = render(
            <ThemeProvider theme={theme}>
                <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                    <DataModel.Provider value={dataModel}>
                        <Report
                            dates={dates}
                            handleSort={handleSort}
                            lastUpdate={new Date()}
                            measurements={[]}
                            reports={[reportToRender]}
                            report={reportToRender}
                            report_date={report_date}
                            settings={settings}
                        />
                    </DataModel.Provider>
                </Permissions.Provider>
            </ThemeProvider>,
        )
    })
    return result
}

it("shows the report", async () => {
    const { container } = await renderReport({ reportToRender: report })
    expect(screen.getAllByText(/Subject title/).length).toBe(2) // Once as dashboard card and once as subject header
    await expectNoAccessibilityViolations(container)
})

it("shows an error message if there is no report", async () => {
    const { container } = await renderReport()
    expect(screen.getAllByText(/Sorry, this report doesn't exist/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows an error message if there was no report", async () => {
    const { container } = await renderReport({ report_date: new Date("2020-01-01") })
    expect(screen.getAllByText(/Sorry, this report didn't exist/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("hides columns on load", async () => {
    history.push("?hidden_columns=status")
    await renderReport({ reportToRender: report })
    expect(screen.queryByText(/Status/)).toBe(null)
})

it("sorts the column", async () => {
    let handleSort = vi.fn()
    await renderReport({ reportToRender: report, handleSort: handleSort })
    fireEvent.click(screen.getByText(/Comment/))
    expect(handleSort).toHaveBeenCalledWith("comment")
})

it("sorts the column descending", async () => {
    history.push("?sort_column=comment")
    let handleSort = vi.fn()
    await renderReport({ reportToRender: report, handleSort: handleSort })
    fireEvent.click(screen.getByText(/Comment/))
    expect(handleSort).toHaveBeenCalledWith("comment")
})

it("stops sorting", async () => {
    history.push("?sort_column=issues&sort_direction=descending")
    let handleSort = vi.fn()
    await renderReport({ reportToRender: report, handleSort: handleSort })
    fireEvent.click(screen.getByText(/Issues/))
    expect(handleSort).toHaveBeenCalledWith("issues")
})

it("stop sorting on add metric", async () => {
    history.push("?sort_column=status")
    let handleSort = vi.fn()
    await renderReport({ reportToRender: report, handleSort: handleSort })
    fireEvent.click(screen.getByText(/Add metric/))
    fireEvent.click(screen.getByText(/Metric type/))
    expect(handleSort).toHaveBeenCalledWith(null)
})

it("sorts another column", async () => {
    history.push("?sort_column=issues")
    let handleSort = vi.fn()
    await renderReport({ reportToRender: report, handleSort: handleSort })
    fireEvent.click(screen.getByText(/Comment/))
    expect(handleSort).toHaveBeenCalledWith("comment")
})

it("hides tags", async () => {
    const hiddenTags = renderHook(() => useHiddenTagsURLSearchQuery())
    await renderReport({ reportToRender: report, hiddenTags: hiddenTags.result.current })
    fireEvent.click(screen.getAllByText(/tag/)[0])
    hiddenTags.rerender()
    expect(hiddenTags.result.current.value).toStrictEqual(["other"])
})

it("shows hidden tags", async () => {
    history.push("?hidden_tags=other")
    const hiddenTags = renderHook(() => useHiddenTagsURLSearchQuery())
    await renderReport({ reportToRender: report, hiddenTags: hiddenTags.result.current })
    expect(screen.queryAllByText("other").length).toBe(0)
    fireEvent.click(screen.getAllByText(/tag/)[0])
    hiddenTags.rerender()
    expect(hiddenTags.result.current.value).toStrictEqual([])
})

it("hides subjects if empty", async () => {
    history.push("?hidden_tags=tag,other")
    await renderReport({ reportToRender: report })
    expect(screen.queryAllByText(/Subject title/).length).toBe(0)
})

it("navigates to subject", async () => {
    const mockScroll = vi.fn()
    window.HTMLElement.prototype.scrollIntoView = mockScroll
    const mockScrollBy = vi.fn()
    window.scrollBy = mockScrollBy
    await renderReport({ reportToRender: report })
    fireEvent.click(screen.getAllByText(/Subject title/)[0])
    expect(mockScroll).toHaveBeenCalledWith()
    expect(mockScrollBy).toHaveBeenCalledWith(0, 163)
})
