import { act, fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectFetch, expectNoAccessibilityViolations } from "../testUtils"
import { Tags } from "./Tags"

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true })
})

function renderTags({ tags = ["foo"] } = {}) {
    return render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <Tags
                report={{
                    report_uuid: "report_uuid",
                    title: "Report",
                    subjects: { subject_uuid: { metrics: { metric_uuid: { tags: tags } } } },
                }}
                reload={vi.fn()}
            />
        </Permissions.Provider>,
    )
}

it("shows the tags", async () => {
    const { container } = renderTags()
    expect(screen.getAllByText(/Tag/).length).toBe(1)
    expect(screen.getAllByText(/Number of metrics/).length).toBe(1)
    expect(screen.getAllByText(/foo/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows an info message if there are no tags", async () => {
    const { container } = renderTags({ tags: [] })
    expect(screen.getAllByText(/None of the metrics in this report have tags/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("deletes a tag", async () => {
    const { container } = renderTags()
    await act(async () => {
        fireEvent.click(screen.getAllByLabelText(/Expand/)[0])
    })
    await expectNoAccessibilityViolations(container)
    await act(async () => {
        fireEvent.click(screen.getByText(/Delete tag/))
    })
    expectFetch("delete", "report/report_uuid/tag/foo")
    await expectNoAccessibilityViolations(container)
})

it("renames a tag", async () => {
    const { container } = renderTags()
    await act(async () => {
        fireEvent.click(screen.getAllByLabelText(/Expand/)[0])
    })
    await expectNoAccessibilityViolations(container)
    await userEvent.type(screen.getByLabelText("Tag"), "bar{Enter}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 3,
    })
    expectFetch("post", "report/report_uuid/tag/foo", { tag: "bar" })
    await expectNoAccessibilityViolations(container)
})
