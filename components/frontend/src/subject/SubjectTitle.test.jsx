import { act, fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { useSettings } from "../app_ui_settings"
import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import {
    asyncClickButton,
    asyncClickText,
    clickText,
    expectFetch,
    expectNoAccessibilityViolations,
    expectSearch,
} from "../testUtils"
import { SubjectTitle } from "./SubjectTitle"

beforeEach(() => {
    history.push("?expanded=subject_uuid:0")
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true })
})

afterEach(() => vi.restoreAllMocks())

const dataModel = {
    subjects: {
        subject_type: {
            name: "Default subject type",
            subjects: { nested_subject_type: { name: "Nested subject type" } },
        },
        subject_type2: { name: "Other subject type" },
    },
    metrics: {
        metric_type: { tags: [] },
    },
}
const report = {
    report_uuid: "report_uuid",
    subjects: {
        subject_uuid: {
            type: "subject_type",
            name: "Subject title",
            metrics: { metric_uuid: { type: "metric_type", tags: [] } },
        },
    },
}

function SubjectTitleWrapper({ subjectType }) {
    const settings = useSettings()
    return (
        <PermissionsContext value={[EDIT_REPORT_PERMISSION]}>
            <DataModelContext value={dataModel}>
                <SubjectTitle
                    report={report}
                    settings={settings}
                    subject={{ type: subjectType }}
                    subjectUuid="subject_uuid"
                />
            </DataModelContext>
        </PermissionsContext>
    )
}

async function renderSubjectTitle(subjectType = "subject_type") {
    let result
    await act(async () => {
        result = render(<SubjectTitleWrapper subjectType={subjectType} />)
    })
    return result
}

it("has no accessibility violations", async () => {
    const { container } = await renderSubjectTitle()
    await expectNoAccessibilityViolations(container)
})

it("changes the subject type", async () => {
    await renderSubjectTitle()
    fireEvent.mouseDown(screen.getByLabelText(/Subject type/))
    clickText(/Other subject type/)
    expectFetch("post", "subject/subject_uuid/attribute/type", { type: "subject_type2" })
})

it("changes the subject type to a nested type", async () => {
    await renderSubjectTitle()
    fireEvent.mouseDown(screen.getByLabelText(/Subject type/))
    clickText(/Nested subject type/)
    expectFetch("post", "subject/subject_uuid/attribute/type", { type: "nested_subject_type" })
})

it("changes the subject type from a nested type", async () => {
    await renderSubjectTitle("nested_subject_type")
    fireEvent.mouseDown(screen.getByLabelText(/Subject type/))
    clickText(/Other subject type/)
    expectFetch("post", "subject/subject_uuid/attribute/type", { type: "subject_type2" })
})

it("changes the subject title", async () => {
    await renderSubjectTitle()
    await userEvent.type(screen.getByLabelText(/Subject title/), "New title{Enter}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 100,
    })
    expectFetch("post", "subject/subject_uuid/attribute/name", { name: "New title" })
})

it("changes the subject subtitle", async () => {
    const { container } = await renderSubjectTitle()
    await userEvent.type(screen.getByLabelText(/Subject subtitle/), "{Delete}New subtitle{Enter}")
    expectFetch("post", "subject/subject_uuid/attribute/subtitle", { subtitle: "New subtitle" })
    await expectNoAccessibilityViolations(container)
})

it("changes the subject comment", async () => {
    await renderSubjectTitle()
    await userEvent.type(screen.getByLabelText(/Comment/), "{Delete}New comment{Shift>}{Enter}")
    expectFetch("post", "subject/subject_uuid/attribute/comment", { comment: "New comment" })
})

it("loads the changelog", async () => {
    history.push("?expanded=subject_uuid:1")
    await renderSubjectTitle()
    expectFetch("get", "changelog/subject/subject_uuid/5")
})

it("moves the subject", async () => {
    await renderSubjectTitle()
    await asyncClickButton(/Move subject to the next position/)
    expectFetch("post", "subject/subject_uuid/attribute/position", { position: "next" })
})

it("deletes the subject", async () => {
    history.push("?expanded=subject_uuid:0")
    await renderSubjectTitle()
    await asyncClickText(/Delete subject/)
    expectFetch("delete", "subject/subject_uuid", {})
    expectSearch("")
})

it("uses the name of the subject type for the documentation link", async () => {
    await renderSubjectTitle()
    const readTheDocsLink = screen.getByRole("link", { name: "Read the Docs" })
    expect(readTheDocsLink).toHaveAttribute("href", expect.stringContaining("#default-subject-type"))
})
