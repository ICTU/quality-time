import { act, render } from "@testing-library/react"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { asyncClickText, expectNoAccessibilityViolations } from "../testUtils"
import { SnackbarAlerts } from "../widgets/SnackbarAlerts"
import { ChangeLog } from "./ChangeLog"

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockImplementation(() =>
        Promise.resolve({ changelog: [{ timestamp: "2020-01-01" }] }),
    )
})

function createChangeLog(props) {
    return (
        <SnackbarAlerts messages={[]} showMessage={props?.showMessage ?? vi.fn()}>
            <ChangeLog {...props} />
        </SnackbarAlerts>
    )
}

async function renderChangeLog(props) {
    let result
    await act(async () => {
        result = render(createChangeLog(props))
    })
    return result
}

function expectNrEventsToBe(nr) {
    // Assert that the change log contains nr events
    const rows = document.querySelectorAll(".MuiListItem-root")
    expect(rows).toHaveLength(nr)
}

it("has no accessibility violations", async () => {
    const { container } = render(<ChangeLog reportUuid="uuid" />)
    await expectNoAccessibilityViolations(container)
})

it("renders no changes", async () => {
    fetchServerApi.fetchServerApi.mockImplementation(() => Promise.resolve({ changelog: [] }))
    await renderChangeLog({})
    expectNrEventsToBe(0)
})

it("renders one report change", async () => {
    await renderChangeLog({ reportUuid: "uuid" })
    expectNrEventsToBe(1)
})

it("renders one subject change", async () => {
    await renderChangeLog({ subjectUuid: "uuid" })
    expectNrEventsToBe(1)
})

it("renders one metric change", async () => {
    await renderChangeLog({ metricUuid: "uuid" })
    expectNrEventsToBe(1)
})

it("renders one source change", async () => {
    await renderChangeLog({ sourceUuid: "uuid" })
    expectNrEventsToBe(1)
})

it("loads more changes", async () => {
    await renderChangeLog({ sourceUuid: "uuid" })
    fetchServerApi.fetchServerApi.mockImplementation(() =>
        Promise.resolve({ changelog: [{ timestamp: "2020-01-01" }, { timestamp: "2020-01-02" }] }),
    )
    await asyncClickText(/Load more changes/)
    expectNrEventsToBe(2)
})

it("shows error when loading more changes fails", async () => {
    const showMessage = vi.fn()
    await renderChangeLog({ sourceUuid: "uuid", showMessage: showMessage })
    fetchServerApi.fetchServerApi.mockImplementation(() => Promise.reject(new Error("Couldn't retrieve changelog")))
    await asyncClickText(/Load more changes/)
    expect(showMessage).toHaveBeenCalledTimes(1)
    expectNrEventsToBe(1)
})

it("ignores stale fetch responses when props change", async () => {
    let resolveStale
    fetchServerApi.fetchServerApi
        .mockImplementationOnce(() => new Promise((resolve) => (resolveStale = resolve)))
        .mockImplementation(() =>
            Promise.resolve({ changelog: [{ timestamp: "2020-02-02" }, { timestamp: "2020-02-03" }] }),
        )
    const showMessage = vi.fn()
    const { rerender } = await renderChangeLog({ reportUuid: "uuid1", showMessage })
    await act(async () => rerender(createChangeLog({ reportUuid: "uuid2", showMessage })))
    await act(async () => resolveStale({ changelog: [{ timestamp: "2020-01-01" }] }))
    // The fresh fetch returns 2 events; the stale fetch later resolves with 1 event.
    // Asserting 2 proves the stale response was dropped (didCancel === true).
    // if the cancel guard were missing, the late stale resolution would overwrite state to 1.
    expectNrEventsToBe(2)
})
