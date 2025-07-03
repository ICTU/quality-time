import { LocalizationProvider } from "@mui/x-date-pickers"
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs"
import { act, fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"

import { createTestableSettings } from "../__fixtures__/fixtures"
import { expectNoAccessibilityViolations } from "../testUtils"
import { ReportPeriodPanel } from "./ReportPeriodPanel"

beforeEach(() => {
    history.push("")
})

function renderReportPeriodPanel() {
    const settings = createTestableSettings()
    return render(
        <LocalizationProvider dateAdapter={AdapterDayjs}>
            <ReportPeriodPanel
                settings={{
                    dateInterval: settings.dateInterval,
                    dateOrder: settings.dateOrder,
                    nrDates: settings.nrDates,
                }}
            />
        </LocalizationProvider>,
    )
}

it("sets the number of dates", async () => {
    history.push("?nr_dates=2")
    const { container } = renderReportPeriodPanel()
    fireEvent.click(screen.getByText(/7 dates/))
    expect(history.location.search).toBe("?nr_dates=7")
    await expectNoAccessibilityViolations(container)
})

it("sets the number of dates by keypress", async () => {
    renderReportPeriodPanel()
    await userEvent.type(screen.getByText(/5 dates/), " ")
    expect(history.location.search).toBe("?nr_dates=5")
})

it("sets the date interval to weeks", async () => {
    history.push("?nr_dates=2")
    renderReportPeriodPanel()
    await act(async () => fireEvent.click(screen.getByText(/2 weeks/)))
    expect(history.location.search).toBe("?nr_dates=2&date_interval=14")
})

it("sets the date interval to one day", () => {
    history.push("?nr_dates=2")
    renderReportPeriodPanel()
    fireEvent.click(screen.getByText(/1 day/))
    expect(history.location.search).toBe("?nr_dates=2&date_interval=1")
})

it("sets the date interval by keypress", async () => {
    history.push("?nr_dates=2&date_interval=7")
    renderReportPeriodPanel()
    await userEvent.type(screen.getByText(/1 day/), " ")
    expect(history.location.search).toBe("?nr_dates=2&date_interval=1")
})

it("sorts the dates descending", () => {
    history.push("?nr_dates=2&date_order=ascending")
    renderReportPeriodPanel()
    fireEvent.click(screen.getByText(/Descending/))
    expect(history.location.search).toBe("?nr_dates=2")
})

it("sorts the dates ascending by keypress", async () => {
    history.push("?nr_dates=2")
    renderReportPeriodPanel()
    await userEvent.type(screen.getByText(/Ascending/), " ")
    expect(history.location.search).toBe("?nr_dates=2&date_order=ascending")
})
