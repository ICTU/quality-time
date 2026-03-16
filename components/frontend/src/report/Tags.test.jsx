import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import {
    asyncClickLabeledElement,
    asyncClickText,
    expectFetch,
    expectNoAccessibilityViolations,
    expectText,
} from "../testUtils"
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

it("has no accessibility violations", async () => {
    const { container } = renderTags()
    await expectNoAccessibilityViolations(container)
})

it("shows the tags", async () => {
    renderTags()
    expectText(/Tag/)
    expectText(/Number of metrics/)
    expectText(/foo/)
})

it("shows an info message if there are no tags", async () => {
    renderTags({ tags: [] })
    expectText(/None of the metrics in this report have tags/)
})

it("deletes a tag", async () => {
    renderTags()
    await asyncClickLabeledElement(/Expand/, 0)
    await asyncClickText(/Delete tag/)
    expectFetch("delete", "report/report_uuid/tag/foo")
})

it("renames a tag", async () => {
    renderTags()
    await asyncClickLabeledElement(/Expand/, 0)
    await userEvent.type(screen.getByLabelText("Tag"), "bar{Enter}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 3,
    })
    expectFetch("post", "report/report_uuid/tag/foo", { tag: "bar" })
})
