import { act, fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings } from "../__fixtures__/fixtures"
import * as fetch_server_api from "../api/fetch_server_api"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectNoAccessibilityViolations } from "../testUtils"
import { ReportsOverviewTitle } from "./ReportsOverviewTitle"

vi.mock("../api/fetch_server_api.js")

beforeEach(() => {
    history.push("?expanded=reports_overview")
})

function renderReportsOverviewTitle() {
    return render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <ReportsOverviewTitle reports_overview={{}} settings={createTestableSettings()} />
        </Permissions.Provider>,
    )
}

it("sets the title", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true })
    const { container } = renderReportsOverviewTitle()
    await userEvent.type(screen.getByLabelText(/Report overview title/), "{Delete}New title{Enter}")
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "reports_overview/attribute/title", {
        title: "New title",
    })
    await expectNoAccessibilityViolations(container)
})

it("sets the subtitle", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true })
    const { container } = renderReportsOverviewTitle()
    await userEvent.type(screen.getByLabelText(/Report overview subtitle/), "{Delete}New subtitle{Enter}")
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "reports_overview/attribute/subtitle", {
        subtitle: "New subtitle",
    })
    await expectNoAccessibilityViolations(container)
})

it("sets the comment", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true })
    const { container } = renderReportsOverviewTitle()
    await userEvent.type(screen.getByLabelText(/Comment/), "{Delete}New comment{Shift>}{Enter}")
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "reports_overview/attribute/comment", {
        comment: "New comment",
    })
    await expectNoAccessibilityViolations(container)
})

it("sets the edit report permission", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true })
    const { container } = renderReportsOverviewTitle()
    fireEvent.click(screen.getByText(/Permissions/))
    await userEvent.type(screen.getByLabelText(/Users allowed to edit reports/), "jadoe{Enter}")
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith(
        "post",
        "reports_overview/attribute/permissions",
        { permissions: { edit_reports: ["jadoe"] } },
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the edit entities permission", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true })
    const { container } = renderReportsOverviewTitle()
    fireEvent.click(screen.getByText(/Permissions/))
    await userEvent.type(screen.getByLabelText(/Users allowed to edit measured entities/), "jodoe{Enter}")
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith(
        "post",
        "reports_overview/attribute/permissions",
        { permissions: { edit_entities: ["jodoe"] } },
    )
    await expectNoAccessibilityViolations(container)
})

it("loads the changelog", async () => {
    const { container } = renderReportsOverviewTitle()
    await act(async () => {
        fireEvent.click(screen.getByText(/Changelog/))
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenCalledWith("get", "changelog/5")
    await expectNoAccessibilityViolations(container)
})
