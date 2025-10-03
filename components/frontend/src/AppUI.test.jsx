import { ThemeProvider } from "@mui/material/styles"
import { act, render } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { dataModel, report } from "./__fixtures__/fixtures"
import * as fetchServerApi from "./api/fetch_server_api"
import { AppUI } from "./AppUI"
import { mockGetAnimations } from "./dashboard/MockAnimations"
import {
    asyncClickText,
    clickText,
    expectNoAccessibilityViolations,
    expectNoText,
    expectSearch,
    expectText,
} from "./testUtils"
import { theme } from "./theme"

beforeEach(async () => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockReturnValue({
        then: vi.fn().mockReturnValue({ catch: vi.fn().mockReturnValue({ finally: vi.fn() }) }),
    })
    mockGetAnimations()
    history.push("")
})

afterEach(() => vi.restoreAllMocks())

async function renderAppUI({ reports = [], reportDate = null, reportUuid = "" } = {}) {
    let result
    await act(async () => {
        result = render(
            <ThemeProvider theme={theme}>
                <AppUI
                    dataModel={dataModel}
                    handleDateChange={vi.fn}
                    lastUpdate={new Date()}
                    reportDate={reportDate}
                    reportUuid={reportUuid}
                    reports={reports ?? []}
                    reportsOverview={{}}
                    user="xxx"
                />
            </ThemeProvider>,
        )
    })
    return result
}

it("shows an error message when there are no reports", async () => {
    const { container } = await renderAppUI({ reportDate: new Date() })
    expectText(/Sorry, no reports/)
    await expectNoAccessibilityViolations(container)
})

it("handles sorting", async () => {
    await renderAppUI({ reports: [report], reportUuid: "report_uuid" })
    clickText("Comment", 0)
    expectSearch("?sort_column_report_uuid=comment")
    clickText("Status", 0)
    expectSearch("?sort_column_report_uuid=status")
    clickText("Status", 0)
    expectSearch("?sort_column_report_uuid=status&sort_direction_report_uuid=descending")
    clickText("Status", 0)
    expectSearch("")
    clickText("Comment", 0)
    expectSearch("?sort_column_report_uuid=comment")
    await asyncClickText(/Add metric/, 0)
    await asyncClickText(/Metric type/, 0)
    expectSearch("")
})

it("resets all settings", async () => {
    history.push("?date_interval=2")
    await act(async () => {
        await renderAppUI()
    })
    clickText("Reset settings")
    expectSearch("")
})

it("shows all tags of all reports in the settings menu at the reports overview", async () => {
    await renderAppUI({
        reports: [
            {
                report_uuid: "report_uuid1",
                subjects: { subject_uuid1: { metrics: { metric_uuid1: { scale: "count", tags: ["tag1"] } } } },
                title: "Report 1",
            },
            {
                report_uuid: "report_uuid2",
                subjects: { subject_uuid2: { metrics: { metric_uuid2: { scale: "count", tags: ["tag2"] } } } },
                title: "Report 2",
            },
        ],
    })
    expectText("tag1")
    expectText("tag2")
})

it("shows only tags of the current report in the settings menu", async () => {
    await renderAppUI({
        reports: [
            {
                report_uuid: "report_uuid1",
                subjects: {
                    subject_uuid1: {
                        metrics: {
                            metric_uuid1: {
                                direction: "<",
                                name: "Metric 1",
                                scale: "count",
                                tags: ["tag1"],
                                unit: "unit",
                            },
                        },
                    },
                },
                title: "Report 1",
            },
            {
                report_uuid: "report_uuid2",
                subjects: {
                    subject_uuid2: {
                        metrics: {
                            metric_uuid2: {
                                direction: "<",
                                name: "Metric 2",
                                scale: "count",
                                tags: ["tag2"],
                                unit: "unit",
                            },
                        },
                    },
                },
                title: "Report 2",
            },
        ],
        reportUuid: "report_uuid1",
    })
    clickText("Settings")
    expectText("tag1", 3)
    expectNoText("tag2")
})
