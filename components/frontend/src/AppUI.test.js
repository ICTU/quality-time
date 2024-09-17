import { act, fireEvent, render, screen } from "@testing-library/react"
import history from "history/browser"

import { dataModel, report } from "./__fixtures__/fixtures"
import * as fetch_server_api from "./api/fetch_server_api"
import { AppUI } from "./AppUI"
import { mockGetAnimations } from "./dashboard/MockAnimations"

beforeEach(() => {
    fetch_server_api.fetch_server_api = jest.fn().mockReturnValue({
        then: jest.fn().mockReturnValue({ catch: jest.fn().mockReturnValue({ finally: jest.fn() }) }),
    })
    mockGetAnimations()
    history.push("")
})

afterEach(() => jest.restoreAllMocks())

it("shows an error message when there are no reports", async () => {
    await act(async () => render(<AppUI report_uuid="" reports={[]} reports_overview={{}} />))
    expect(screen.getAllByText(/Sorry, no reports/).length).toBe(1)
})

it("handles sorting", async () => {
    await act(async () =>
        render(
            <AppUI
                dataModel={dataModel}
                lastUpdate={new Date()}
                report_date={null}
                report_uuid="report_uuid"
                reports={[report]}
                reports_overview={{}}
                user="xxx"
            />,
        ),
    )
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

async function renderAppUI() {
    return await act(async () =>
        render(<AppUI handleDateChange={jest.fn} report_uuid="" reports={[]} reports_overview={{}} />),
    )
}

it("resets all settings", async () => {
    history.push("?date_interval=2")
    await act(async () => await renderAppUI())
    fireEvent.click(screen.getByLabelText("Reset reports overview settings"))
    expect(history.location.search).toBe("")
})
