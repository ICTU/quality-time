import { act, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { useSettings } from "../app_ui_settings"
import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import { expectFetch, expectNoAccessibilityViolations } from "../testUtils"
import { ReportsOverviewTitle } from "./ReportsOverviewTitle"

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true })
    history.push("?expanded=reports_overview:0")
})

afterEach(() => vi.restoreAllMocks())

function ReportsOverviewTitleWrapper() {
    const settings = useSettings()
    return (
        <PermissionsContext value={[EDIT_REPORT_PERMISSION]}>
            <ReportsOverviewTitle reportsOverview={{}} settings={settings} />
        </PermissionsContext>
    )
}

function renderReportsOverviewTitle() {
    return render(<ReportsOverviewTitleWrapper />)
}

it("has no accessibility violations", async () => {
    const { container } = renderReportsOverviewTitle()
    await expectNoAccessibilityViolations(container)
})

it("sets the title", async () => {
    renderReportsOverviewTitle()
    await userEvent.type(screen.getByLabelText(/Report overview title/), "{Delete}New title{Enter}")
    expectFetch("post", "reports_overview/attribute/title", { title: "New title" })
})

it("sets the subtitle", async () => {
    renderReportsOverviewTitle()
    await userEvent.type(screen.getByLabelText(/Report overview subtitle/), "{Delete}New subtitle{Enter}")
    expectFetch("post", "reports_overview/attribute/subtitle", { subtitle: "New subtitle" })
})

it("sets the comment", async () => {
    renderReportsOverviewTitle()
    await userEvent.type(screen.getByLabelText(/Comment/), "{Delete}New comment{Shift>}{Enter}")
    expectFetch("post", "reports_overview/attribute/comment", { comment: "New comment" })
})

it("sets the edit report permission", async () => {
    history.push("?expanded=reports_overview:1")
    renderReportsOverviewTitle()
    await userEvent.type(screen.getByLabelText(/Users allowed to edit reports/), "jadoe{Enter}")
    expectFetch("post", "reports_overview/attribute/permissions", { permissions: { edit_reports: ["jadoe"] } })
})

it("sets the edit entities permission", async () => {
    history.push("?expanded=reports_overview:1")
    renderReportsOverviewTitle()
    await userEvent.type(screen.getByLabelText(/Users allowed to edit measured entities/), "jodoe{Enter}")
    expectFetch("post", "reports_overview/attribute/permissions", { permissions: { edit_entities: ["jodoe"] } })
})

it("loads the changelog", async () => {
    history.push("?expanded=reports_overview:2")
    renderReportsOverviewTitle()
    await act(async () => expectFetch("get", "changelog/5"))
})
