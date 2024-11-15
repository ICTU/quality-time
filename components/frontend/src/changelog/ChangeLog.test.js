import { act, fireEvent, render, screen, waitFor } from "@testing-library/react"

import * as changelog_api from "../api/changelog"
import * as toast from "../widgets/toast"
import { ChangeLog } from "./ChangeLog"

jest.mock("../api/changelog.js")
jest.mock("../widgets/toast.js")

beforeEach(() => {
    jest.resetAllMocks()
})

function expectNrEventsToBe(nr) {
    // Assert that the change log contains nr events
    const rows = document.querySelectorAll(".MuiListItem-root")
    expect(rows.length).toBe(nr)
}

it("renders no changes", async () => {
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [] }))
    await act(async () => {
        render(<ChangeLog />)
    })
    expectNrEventsToBe(0)
})

it("renders one report change", async () => {
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [{ timestamp: "2020-01-01" }] }))
    await act(async () => {
        render(<ChangeLog report_uuid="uuid" />)
    })
    expectNrEventsToBe(1)
})

it("renders one subject change", async () => {
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [{ timestamp: "2020-01-01" }] }))
    await act(async () => {
        render(<ChangeLog subject_uuid="uuid" />)
    })
    expectNrEventsToBe(1)
})

it("renders one metric change", async () => {
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [{ timestamp: "2020-01-01" }] }))
    await act(async () => {
        render(<ChangeLog metric_uuid="uuid" />)
    })
    expectNrEventsToBe(1)
})

it("renders one source change", async () => {
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [{ timestamp: "2020-01-01" }] }))
    await act(async () => {
        render(<ChangeLog source_uuid="uuid" />)
    })
    expectNrEventsToBe(1)
})

it("loads more changes", async () => {
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [{ timestamp: "2020-01-01" }] }))
    await act(async () => {
        render(<ChangeLog source_uuid="uuid" />)
    })
    changelog_api.get_changelog.mockImplementation(() =>
        Promise.resolve({ changelog: [{ timestamp: "2020-01-01" }, { timestamp: "2020-01-02" }] }),
    )
    await act(async () => fireEvent.click(screen.getByText(/Load more changes/)))
    expectNrEventsToBe(2)
})

it("shows error when loading more changes fails", async () => {
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [] }))
    await act(async () => {
        render(<ChangeLog source_uuid="uuid" />)
    })
    changelog_api.get_changelog.mockImplementation(() => Promise.reject(new Error("Couldn't retrieve changelog")))
    await act(async () => fireEvent.click(screen.getByText(/Load more changes/)))
    await waitFor(() => {
        expect(toast.showMessage).toHaveBeenCalledTimes(1)
    })
    expectNrEventsToBe(0)
})
