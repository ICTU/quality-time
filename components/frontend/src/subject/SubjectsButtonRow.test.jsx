import { render, screen } from "@testing-library/react"
import { vi } from "vitest"

import { createTestableSettings, dataModel, report } from "../__fixtures__/fixtures"
import * as fetchServerApi from "../api/fetch_server_api"
import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
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
        <PermissionsContext value={permissions}>
            <DataModelContext value={dataModel}>
                <SubjectsButtonRow report={report} reports={[report]} settings={createTestableSettings()} />
            </DataModelContext>
        </PermissionsContext>,
    )
}

it("has no accessibility violations", async () => {
    const { container } = renderSubjectsButtonRow()
    await expectNoAccessibilityViolations(container)
})

it("shows the add subject button when editable", async () => {
    renderSubjectsButtonRow([EDIT_REPORT_PERMISSION])
    expectText(/Add subject/)
})

it("does not show the add subject button when not editable", () => {
    renderSubjectsButtonRow()
    expect(screen.queryByText(/Add subject/)).toBeNull()
})

it("adds a subject", async () => {
    renderSubjectsButtonRow([EDIT_REPORT_PERMISSION])
    await asyncClickText(/Add subject/)
    await asyncClickText(/Subject type/)
    expectFetch("post", "subject/new/report_uuid", { type: "subject_type" })
})

it("copies a subject", async () => {
    renderSubjectsButtonRow([EDIT_REPORT_PERMISSION])
    await asyncClickText("Copy subject")
    await asyncClickText("dummy option 1")
    expectFetch("post", "subject/undefined/copy/report_uuid", {})
})

it("moves a subject", async () => {
    renderSubjectsButtonRow([EDIT_REPORT_PERMISSION])
    await asyncClickText("Move subject")
    await asyncClickText("dummy option 2")
    expectFetch("post", "subject/undefined/move/report_uuid", {})
})
