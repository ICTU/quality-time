import { act, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { vi } from "vitest"

import * as changelogApi from "../api/changelog"
import { expectNoAccessibilityViolations } from "../testUtils"
import * as toast from "../widgets/toast"
import { ChangeLog } from "./ChangeLog"

vi.mock("../api/changelog.js")
vi.mock("../widgets/toast.jsx")

beforeEach(() => vi.resetAllMocks())

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
    changelogApi.getChangelog.mockImplementation(() => Promise.resolve({ changelog: [] }))
    const { container } = await renderChangeLog({})
    expectNrEventsToBe(0)
    await expectNoAccessibilityViolations(container)
})

it("renders one report change", async () => {
    changelogApi.getChangelog.mockImplementation(() => Promise.resolve({ changelog: [{ timestamp: "2020-01-01" }] }))
    const { container } = await renderChangeLog({ reportUuid: "uuid" })
    expectNrEventsToBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders one subject change", async () => {
    changelogApi.getChangelog.mockImplementation(() => Promise.resolve({ changelog: [{ timestamp: "2020-01-01" }] }))
    const { container } = await renderChangeLog({ subjectUuid: "uuid" })
    expectNrEventsToBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders one metric change", async () => {
    changelogApi.getChangelog.mockImplementation(() => Promise.resolve({ changelog: [{ timestamp: "2020-01-01" }] }))
    const { container } = await renderChangeLog({ metricUuid: "uuid" })
    expectNrEventsToBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders one source change", async () => {
    changelogApi.getChangelog.mockImplementation(() => Promise.resolve({ changelog: [{ timestamp: "2020-01-01" }] }))
    const { container } = await renderChangeLog({ sourceUuid: "uuid" })
    expectNrEventsToBe(1)
    await expectNoAccessibilityViolations(container)
})

it("loads more changes", async () => {
    changelogApi.getChangelog.mockImplementation(() => Promise.resolve({ changelog: [{ timestamp: "2020-01-01" }] }))
    const { container } = await renderChangeLog({ sourceUuid: "uuid" })
    changelogApi.getChangelog.mockImplementation(() =>
        Promise.resolve({ changelog: [{ timestamp: "2020-01-01" }, { timestamp: "2020-01-02" }] }),
    )
    await act(async () => fireEvent.click(screen.getByText(/Load more changes/)))
    expectNrEventsToBe(2)
    await expectNoAccessibilityViolations(container)
})

it("shows error when loading more changes fails", async () => {
    changelogApi.getChangelog.mockImplementation(() => Promise.resolve({ changelog: [] }))
    const { container } = await renderChangeLog({ sourceUuid: "uuid" })
    changelogApi.getChangelog.mockImplementation(() => Promise.reject(new Error("Couldn't retrieve changelog")))
    await act(async () => fireEvent.click(screen.getByText(/Load more changes/)))
    await waitFor(async () => {
        expect(toast.showMessage).toHaveBeenCalledTimes(1)
        await expectNoAccessibilityViolations(container)
    })
    expectNrEventsToBe(0)
})
