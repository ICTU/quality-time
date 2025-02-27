import { act, fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings } from "../__fixtures__/fixtures"
import * as fetch_server_api from "../api/fetch_server_api"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectNoAccessibilityViolations } from "../testUtils"
import { SubjectTitle } from "./SubjectTitle"

vi.mock("../api/fetch_server_api.js")

beforeEach(() => history.push("?expanded=subject_uuid:0"))

afterEach(() => vi.restoreAllMocks())

const dataModel = {
    subjects: {
        subject_type: { name: "Default subject type" },
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

async function renderSubjectTitle(subject_type = "subject_type") {
    const settings = createTestableSettings()
    let result
    await act(async () => {
        result = render(
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <DataModel.Provider value={dataModel}>
                    <SubjectTitle
                        report={report}
                        settings={settings}
                        subject={{ type: subject_type }}
                        subject_uuid="subject_uuid"
                    />
                </DataModel.Provider>
            </Permissions.Provider>,
        )
    })
    return result
}

it("changes the subject type", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true })
    const { container } = await renderSubjectTitle()
    fireEvent.mouseDown(screen.getByLabelText(/Subject type/))
    //await userEvent.click(screen.getAllByText(/Default subject type/)[1])
    await userEvent.click(screen.getByText(/Other subject type/))
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "subject/subject_uuid/attribute/type", {
        type: "subject_type2",
    })
    await expectNoAccessibilityViolations(container)
})

it("changes the subject title", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true })
    const { container } = await renderSubjectTitle()
    await userEvent.type(screen.getByLabelText(/Subject title/), "{Delete}New title{Enter}")
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "subject/subject_uuid/attribute/name", {
        name: "New title",
    })
    await expectNoAccessibilityViolations(container)
})

it("changes the subject subtitle", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true })
    const { container } = await renderSubjectTitle()
    await userEvent.type(screen.getByLabelText(/Subject subtitle/), "{Delete}New subtitle{Enter}")
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith(
        "post",
        "subject/subject_uuid/attribute/subtitle",
        { subtitle: "New subtitle" },
    )
    await expectNoAccessibilityViolations(container)
})

it("changes the subject comment", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true })
    const { container } = await renderSubjectTitle()
    await userEvent.type(screen.getByLabelText(/Comment/), "{Delete}New comment{Shift>}{Enter}")
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith(
        "post",
        "subject/subject_uuid/attribute/comment",
        { comment: "New comment" },
    )
    await expectNoAccessibilityViolations(container)
})

it("loads the changelog", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true })
    history.push("?expanded=subject_uuid:1")
    const { container } = await renderSubjectTitle()
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", "changelog/subject/subject_uuid/5")
    await expectNoAccessibilityViolations(container)
})

it("moves the subject", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true })
    const { container } = await renderSubjectTitle()
    await act(async () => {
        fireEvent.click(screen.getByRole("button", { name: /Move subject to the next position/ }))
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith(
        "post",
        "subject/subject_uuid/attribute/position",
        { position: "next" },
    )
    await expectNoAccessibilityViolations(container)
})

it("deletes the subject", async () => {
    history.push("?expanded=subject_uuid:0")
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true })
    const { container } = await renderSubjectTitle()
    await act(async () => {
        fireEvent.click(screen.getByText(/Delete subject/))
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("delete", "subject/subject_uuid", {})
    expect(history.location.search).toEqual("")
    await expectNoAccessibilityViolations(container)
})
