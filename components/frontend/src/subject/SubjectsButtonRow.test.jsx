import { render, screen } from "@testing-library/react"
import { vi } from "vitest"

import { createTestableSettings, dataModel, report } from "../__fixtures__/fixtures"
import * as fetchServerApi from "../api/fetch_server_api"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { asyncClickText, expectFetch, expectNoAccessibilityViolations, expectText } from "../testUtils"
import * as subject from "../widgets/menu_options"
import { SubjectsButtonRow } from "./SubjectsButtonRow"

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockReturnValue({ then: vi.fn().mockReturnValue({ finally: vi.fn() }) })
    vi.spyOn(subject, "subjectOptions").mockReturnValue([
        { key: "1", text: "dummy option 1", content: "dummy option 1" },
        { key: "2", text: "dummy option 2", content: "dummy option 2" },
    ])
})

afterEach(() => vi.clearAllMocks())

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
    expectText(/Add subject/)
    await expectNoAccessibilityViolations(container)
})

it("does not show the add subject button when not editable", () => {
    renderSubjectsButtonRow()
    expect(screen.queryByText(/Add subject/)).toBeNull()
})

it("adds a subject", async () => {
    const { container } = renderSubjectsButtonRow([EDIT_REPORT_PERMISSION])
    await asyncClickText(/Add subject/)
    await expectNoAccessibilityViolations(container)
    await asyncClickText(/Subject type/)
    expectFetch("post", "subject/new/report_uuid", { type: "subject_type" })
})

it("copies a subject", async () => {
    const { container } = renderSubjectsButtonRow([EDIT_REPORT_PERMISSION])
    await asyncClickText("Copy subject")
    await expectNoAccessibilityViolations(container)
    await asyncClickText("dummy option 1")
    expectFetch("post", "subject/undefined/copy/report_uuid", {})
})

it("moves a subject", async () => {
    const { container } = renderSubjectsButtonRow([EDIT_REPORT_PERMISSION])
    await asyncClickText("Move subject")
    await expectNoAccessibilityViolations(container)
    await asyncClickText("dummy option 2")
    expectFetch("post", "subject/undefined/move/report_uuid", {})
})
