import { act, fireEvent, render, screen } from "@testing-library/react"

import { createTestableSettings, datamodel, report } from "../__fixtures__/fixtures"
import * as fetch_server_api from "../api/fetch_server_api"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { SubjectsButtonRow } from "./SubjectsButtonRow"

jest.mock("../api/fetch_server_api.js")

jest.mock("../widgets/menu_options", () => {
    const originalModule = jest.requireActual("../api/subject")

    return {
        __esModule: true,
        ...originalModule,
        subject_options: jest.fn(() => [
            { key: "1", text: "dummy option 1" },
            { key: "2", text: "dummy option 2" },
        ]),
    }
})

beforeEach(() => {
    jest.clearAllMocks()
    fetch_server_api.fetch_server_api = jest
        .fn()
        .mockReturnValue({ then: jest.fn().mockReturnValue({ finally: jest.fn() }) })
})

function renderSubjectsButtonRow(permissions = []) {
    render(
        <Permissions.Provider value={permissions}>
            <DataModel.Provider value={datamodel}>
                <SubjectsButtonRow report={report} reports={[report]} settings={createTestableSettings()} />
            </DataModel.Provider>
        </Permissions.Provider>,
    )
}

it("shows the add subject button when editable", () => {
    renderSubjectsButtonRow([EDIT_REPORT_PERMISSION])
    expect(screen.getAllByText(/Add subject/).length).toBe(1)
})

it("does not show the add subject button when not editable", () => {
    renderSubjectsButtonRow()
    expect(screen.queryByText(/Add subject/)).toBeNull()
})

it("adds a subject", async () => {
    renderSubjectsButtonRow([EDIT_REPORT_PERMISSION])
    await act(async () => fireEvent.click(screen.getByText(/Add subject/)))
    await act(async () => fireEvent.click(screen.getByText(/Subject type/)))
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "subject/new/report_uuid", {
        type: "subject_type",
    })
})

it("copies a subject", async () => {
    renderSubjectsButtonRow([EDIT_REPORT_PERMISSION])
    await act(async () => fireEvent.click(screen.getByText("Copy subject")))
    await act(async () => fireEvent.click(screen.getByText("dummy option 1")))
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "subject/undefined/copy/report_uuid", {})
})

it("moves a subject", async () => {
    renderSubjectsButtonRow([EDIT_REPORT_PERMISSION])
    await act(async () => fireEvent.click(screen.getByText("Move subject")))
    await act(async () => fireEvent.click(screen.getByText("dummy option 2")))
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "subject/undefined/move/report_uuid", {})
})
