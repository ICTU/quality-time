import { act, render, waitFor } from "@testing-library/react"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { asyncClickText, expectNoAccessibilityViolations } from "../testUtils"
import * as toast from "../widgets/toast"
import { ChangeLog } from "./ChangeLog"

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockImplementation(() =>
        Promise.resolve({ changelog: [{ timestamp: "2020-01-01" }] }),
    )
})

async function renderChangeLog({ props }) {
    let result
    await act(async () => {
        result = render(<ChangeLog {...props} />)
    })
    return result
}

function expectNrEventsToBe(nr) {
    // Assert that the change log contains nr events
    const rows = document.querySelectorAll(".MuiListItem-root")
    expect(rows.length).toBe(nr)
}

it("renders no changes", async () => {
    fetchServerApi.fetchServerApi.mockImplementation(() => Promise.resolve({ changelog: [] }))
    const { container } = await renderChangeLog({})
    expectNrEventsToBe(0)
    await expectNoAccessibilityViolations(container)
})

it("renders one report change", async () => {
    const { container } = await renderChangeLog({ reportUuid: "uuid" })
    expectNrEventsToBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders one subject change", async () => {
    const { container } = await renderChangeLog({ subjectUuid: "uuid" })
    expectNrEventsToBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders one metric change", async () => {
    const { container } = await renderChangeLog({ metricUuid: "uuid" })
    expectNrEventsToBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders one source change", async () => {
    const { container } = await renderChangeLog({ sourceUuid: "uuid" })
    expectNrEventsToBe(1)
    await expectNoAccessibilityViolations(container)
})

it("loads more changes", async () => {
    const { container } = await renderChangeLog({ sourceUuid: "uuid" })
    fetchServerApi.fetchServerApi.mockImplementation(() =>
        Promise.resolve({ changelog: [{ timestamp: "2020-01-01" }, { timestamp: "2020-01-02" }] }),
    )
    await asyncClickText(/Load more changes/)
    expectNrEventsToBe(2)
    await expectNoAccessibilityViolations(container)
})

it("shows error when loading more changes fails", async () => {
    const { container } = await renderChangeLog({ sourceUuid: "uuid" })
    fetchServerApi.fetchServerApi.mockImplementation(() => Promise.reject(new Error("Couldn't retrieve changelog")))
    const showMessage = vi.spyOn(toast, "showMessage")
    await asyncClickText(/Load more changes/)
    await waitFor(async () => {
        expect(showMessage).toHaveBeenCalledTimes(1)
        await expectNoAccessibilityViolations(container)
    })
    expectNrEventsToBe(1)
})
