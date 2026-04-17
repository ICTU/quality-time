import { LocalizationProvider } from "@mui/x-date-pickers"
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs"
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"

import { useSettings } from "../app_ui_settings"
import { asyncClickText, clickText, expectNoAccessibilityViolations, expectSearch } from "../testUtils"
import { ReportPeriodPanel } from "./ReportPeriodPanel"

beforeEach(() => {
    history.push("")
})

function ReportPeriodPanelWrapper() {
    const settings = useSettings()
    return (
        <LocalizationProvider dateAdapter={AdapterDayjs}>
            <ReportPeriodPanel settings={settings} />
        </LocalizationProvider>
    )
}

function renderReportPeriodPanel() {
    return render(<ReportPeriodPanelWrapper />)
}

it("has no accessibility violations", async () => {
    const { container } = renderReportPeriodPanel()
    await expectNoAccessibilityViolations(container)
})

it("sets the number of dates", async () => {
    history.push("?nr_dates=2")
    renderReportPeriodPanel()
    clickText(/7 dates/)
    expectSearch("?nr_dates=7")
})

it("sets the number of dates by keypress", async () => {
    renderReportPeriodPanel()
    await userEvent.type(screen.getByText(/5 dates/), " ")
    expectSearch("?nr_dates=5")
})

it("sets the date interval to weeks", async () => {
    history.push("?nr_dates=2")
    renderReportPeriodPanel()
    await asyncClickText(/2 weeks/)
    expectSearch("?nr_dates=2&date_interval=14")
})

it("sets the date interval to one day", () => {
    history.push("?nr_dates=2")
    renderReportPeriodPanel()
    clickText(/1 day/)
    expectSearch("?nr_dates=2&date_interval=1")
})

it("sets the date interval by keypress", async () => {
    history.push("?nr_dates=2&date_interval=7")
    renderReportPeriodPanel()
    await userEvent.type(screen.getByText(/1 day/), " ")
    expectSearch("?nr_dates=2&date_interval=1")
})

it("sorts the dates descending", () => {
    history.push("?nr_dates=2&date_order=ascending")
    renderReportPeriodPanel()
    clickText(/Descending/)
    expectSearch("?nr_dates=2")
})

it("sorts the dates ascending by keypress", async () => {
    history.push("?nr_dates=2")
    renderReportPeriodPanel()
    await userEvent.type(screen.getByText(/Ascending/), " ")
    expectSearch("?nr_dates=2&date_order=ascending")
})
