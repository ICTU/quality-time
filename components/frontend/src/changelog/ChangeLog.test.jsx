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

async function renderChangeLog(props) {
    let result
    await act(async () => {
        result = render(
            <SnackbarAlerts messages={[]} showMessage={props?.showMessage ?? vi.fn()}>
                <ChangeLog {...props} />
            </SnackbarAlerts>,
        )
    })
    return result
}

function expectNrEventsToBe(nr) {
    // Assert that the change log contains nr events
    const rows = document.querySelectorAll(".MuiListItem-root")
    expect(rows.length).toBe(nr)
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
