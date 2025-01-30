import { ThemeProvider } from "@mui/material/styles"
import { act, fireEvent, render, screen } from "@testing-library/react"
import history from "history/browser"
import { axe } from "jest-axe"
import { vi } from "vitest"

import { dataModel, report } from "./__fixtures__/fixtures"
import * as fetch_server_api from "./api/fetch_server_api"
import { AppUI } from "./AppUI"
import { mockGetAnimations } from "./dashboard/MockAnimations"
import { theme } from "./theme"

vi.mock("./api/fetch_server_api.js")

beforeEach(async () => {
    fetch_server_api.api_with_report_date = (await vi.importActual("./api/fetch_server_api.js")).api_with_report_date
    fetch_server_api.fetch_server_api = vi.fn().mockReturnValue({
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
                    report_date={reports ? null : undefined}
                    report_uuid={reports ? "report_uuid" : ""}
                    reports={reports ?? []}
                    reports_overview={{}}
                    user="xxx"
                />
            </ThemeProvider>,
        )
    })
    return result
}

it("shows an error message when there are no reports", async () => {
    const { container } = await renderAppUI()
    expect(screen.getAllByText(/Sorry, no reports/).length).toBe(1)
    expect(await axe(container)).toHaveNoViolations()
})

it("handles sorting", async () => {
    await renderAppUI([report])
    fireEvent.click(screen.getAllByText("Comment")[0])
    expect(history.location.search).toEqual("?sort_column_report_uuid=comment")
    fireEvent.click(screen.getAllByText("Status")[0])
    expect(history.location.search).toEqual("?sort_column_report_uuid=status")
    fireEvent.click(screen.getAllByText("Status")[0])
    expect(history.location.search).toEqual("?sort_column_report_uuid=status&sort_direction_report_uuid=descending")
    fireEvent.click(screen.getAllByText("Status")[0])
    expect(history.location.search).toEqual("")
    fireEvent.click(screen.getAllByText("Comment")[0])
    expect(history.location.search).toEqual("?sort_column_report_uuid=comment")
    await act(async () => fireEvent.click(screen.getAllByText(/Add metric/)[0]))
    await act(async () => fireEvent.click(screen.getAllByText(/Metric type/)[0]))
    expect(history.location.search).toEqual("")
})

it("resets all settings", async () => {
    history.push("?date_interval=2")
    const { container } = await renderAppUI()
    expect(await axe(container)).toHaveNoViolations()
    fireEvent.click(screen.getByText("Reset settings"))
    expect(history.location.search).toBe("")
})
