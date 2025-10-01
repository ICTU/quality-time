import { ThemeProvider } from "@mui/material/styles"
import { act, render } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import { dataModel, report } from "./__fixtures__/fixtures"
import * as fetchServerApi from "./api/fetch_server_api"
import { AppUI } from "./AppUI"
import { mockGetAnimations } from "./dashboard/MockAnimations"
import { asyncClickText, clickText, expectNoAccessibilityViolations, expectSearch, expectText } from "./testUtils"
import { theme } from "./theme"

beforeEach(async () => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockReturnValue({
        then: vi.fn().mockReturnValue({ catch: vi.fn().mockReturnValue({ finally: vi.fn() }) }),
    })
    mockGetAnimations()
    history.push("")
})

afterEach(() => vi.restoreAllMocks())

async function renderAppUI(reports) {
    let result
    await act(async () => {
        result = render(
            <ThemeProvider theme={theme}>
                <AppUI
                    dataModel={dataModel}
                    handleDateChange={vi.fn}
                    lastUpdate={new Date()}
                    reportDate={reports ? null : undefined}
                    reportUuid={reports ? "report_uuid" : ""}
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
    const { container } = await renderAppUI()
    expectText(/Sorry, no reports/)
    await expectNoAccessibilityViolations(container)
})

it("handles sorting", async () => {
    await renderAppUI([report])
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
    const { container } = await renderAppUI()
    await expectNoAccessibilityViolations(container)
    clickText("Reset settings")
    expectSearch("")
})
