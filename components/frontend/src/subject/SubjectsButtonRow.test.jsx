import { act, fireEvent, render, screen } from "@testing-library/react"
import { vi } from "vitest"

import { createTestableSettings, dataModel, report } from "../__fixtures__/fixtures"
import * as fetch_server_api from "../api/fetch_server_api"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectNoAccessibilityViolations } from "../testUtils"
import { SubjectsButtonRow } from "./SubjectsButtonRow"

vi.mock("../api/fetch_server_api.js")

vi.mock("../widgets/menu_options", async () => {
    const originalModule = await vi.importActual("../api/subject.js")

    return {
        __esModule: true,
        ...originalModule,
        subject_options: vi.fn(() => [
            { key: "1", text: "dummy option 1", content: "dummy option 1" },
            { key: "2", text: "dummy option 2", content: "dummy option 2" },
        ]),
    }
})

beforeEach(() => {
    fetch_server_api.fetch_server_api = vi.fn().mockReturnValue({ then: vi.fn().mockReturnValue({ finally: vi.fn() }) })
})

afterEach(() => {
    vi.clearAllMocks()
})

function renderSubjectsButtonRow(permissions = []) {
    return render(
        <Permissions.Provider value={permissions}>
            <DataModel.Provider value={dataModel}>
                <SubjectsButtonRow report={report} reports={[report]} settings={createTestableSettings()} />
            </DataModel.Provider>
        </Permissions.Provider>,
    )
}

it("shows the add subject button when editable", async () => {
    const { container } = renderSubjectsButtonRow([EDIT_REPORT_PERMISSION])
    expect(screen.getAllByText(/Add subject/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("does not show the add subject button when not editable", () => {
    renderSubjectsButtonRow()
    expect(screen.queryByText(/Add subject/)).toBeNull()
})

it("adds a subject", async () => {
    const { container } = renderSubjectsButtonRow([EDIT_REPORT_PERMISSION])
    await act(async () => fireEvent.click(screen.getByText(/Add subject/)))
    await expectNoAccessibilityViolations(container)
    await act(async () => fireEvent.click(screen.getByText(/Subject type/)))
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "subject/new/report_uuid", {
        type: "subject_type",
    })
})

it("copies a subject", async () => {
    const { container } = renderSubjectsButtonRow([EDIT_REPORT_PERMISSION])
    await act(async () => fireEvent.click(screen.getByText("Copy subject")))
    await expectNoAccessibilityViolations(container)
    await act(async () => fireEvent.click(screen.getByText("dummy option 1")))
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "subject/undefined/copy/report_uuid", {})
})

it("moves a subject", async () => {
    const { container } = renderSubjectsButtonRow([EDIT_REPORT_PERMISSION])
    await act(async () => fireEvent.click(screen.getByText("Move subject")))
    await expectNoAccessibilityViolations(container)
    await act(async () => fireEvent.click(screen.getByText("dummy option 2")))
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "subject/undefined/move/report_uuid", {})
})
