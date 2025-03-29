import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings } from "../__fixtures__/fixtures"
import * as fetchServerApi from "../api/fetch_server_api"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectNoAccessibilityViolations } from "../testUtils"
import { ReportsOverviewTitle } from "./ReportsOverviewTitle"

vi.mock("../api/fetch_server_api.js")

beforeEach(() => {
    fetchServerApi.fetchServerApi = vi.fn().mockResolvedValue({ ok: true })
    history.push("?expanded=reports_overview:0")
})

afterEach(() => vi.restoreAllMocks())

function renderReportsOverviewTitle() {
    return render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <ReportsOverviewTitle reportsOverview={{}} settings={createTestableSettings()} />
        </Permissions.Provider>,
    )
}

it("sets the title", async () => {
    const { container } = renderReportsOverviewTitle()
    await userEvent.type(screen.getByLabelText(/Report overview title/), "{Delete}New title{Enter}")
    expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith("post", "reports_overview/attribute/title", {
        title: "New title",
    })
    await expectNoAccessibilityViolations(container)
})

it("sets the subtitle", async () => {
    const { container } = renderReportsOverviewTitle()
    await userEvent.type(screen.getByLabelText(/Report overview subtitle/), "{Delete}New subtitle{Enter}")
    expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith("post", "reports_overview/attribute/subtitle", {
        subtitle: "New subtitle",
    })
    await expectNoAccessibilityViolations(container)
})

it("sets the comment", async () => {
    const { container } = renderReportsOverviewTitle()
    await userEvent.type(screen.getByLabelText(/Comment/), "{Delete}New comment{Shift>}{Enter}")
    expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith("post", "reports_overview/attribute/comment", {
        comment: "New comment",
    })
    await expectNoAccessibilityViolations(container)
})

it("sets the edit report permission", async () => {
    history.push("?expanded=reports_overview:1")
    const { container } = renderReportsOverviewTitle()
    await userEvent.type(screen.getByLabelText(/Users allowed to edit reports/), "jadoe{Enter}")
    expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith("post", "reports_overview/attribute/permissions", {
        permissions: { edit_reports: ["jadoe"] },
    })
    await expectNoAccessibilityViolations(container)
})

it("sets the edit entities permission", async () => {
    history.push("?expanded=reports_overview:1")
    const { container } = renderReportsOverviewTitle()
    await userEvent.type(screen.getByLabelText(/Users allowed to edit measured entities/), "jodoe{Enter}")
    expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith("post", "reports_overview/attribute/permissions", {
        permissions: { edit_entities: ["jodoe"] },
    })
    await expectNoAccessibilityViolations(container)
})

it("loads the changelog", async () => {
    history.push("?expanded=reports_overview:2")
    const { container } = renderReportsOverviewTitle()
    expect(fetchServerApi.fetchServerApi).toHaveBeenCalledWith("get", "changelog/5")
    await expectNoAccessibilityViolations(container)
})
