import { fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectNoAccessibilityViolations } from "../testUtils"
import * as toast from "../widgets/toast"
import { IssuesRows } from "./IssuesRows"

beforeAll(() => vi.spyOn(fetchServerApi, "fetchServerApi"))

const reportWithIssueTracker = {
    issue_tracker: {
        type: "Jira",
        parameters: { url: "https://jira", project_key: "KEY", issue_type: "Bug" },
    },
}

function renderIssuesRow({
    issueIds = [],
    report = { subjects: {} },
    permissions = [EDIT_REPORT_PERMISSION],
    issueStatus = [],
} = {}) {
    return render(
        <Permissions.Provider value={permissions}>
            <IssuesRows
                metric={{
                    type: "violations",
                    issue_ids: issueIds,
                    issue_status: issueStatus,
                }}
                metricUuid="metric_uuid"
                reload={() => {
                    /* Can't use vi.fn here; it leads to "Error: cannot spy on a non-function value" */
                }}
                report={report}
            />
        </Permissions.Provider>,
    )
}

it("does not show an error message if the metric has no issues and no issue tracker is configured", async () => {
    const { container } = renderIssuesRow()
    expect(screen.queryAllByText(/No issue tracker configured/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("does not show an error message if the metric has no issues and an issue tracker is configured", async () => {
    const { container } = renderIssuesRow({ report: { issue_tracker: { type: "Jira" } } })
    expect(screen.queryAllByText(/No issue tracker configured/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("does not show an error message if the metric has issues and an issue tracker is configured", async () => {
    const { container } = renderIssuesRow({
        issueIds: ["BAR-42"],
        report: {
            issue_tracker: {
                type: "Jira",
                parameters: { url: "https://jira", project_key: "KEY", issue_type: "Bug" },
            },
        },
    })
    expect(screen.queryAllByText(/No issue tracker configured/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("shows an error message if the metric has issues but no issue tracker is configured", async () => {
    const { container } = renderIssuesRow({ issueIds: ["FOO-42"] })
    expect(screen.queryAllByText(/No issue tracker configured/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows a connection error", async () => {
    const { container } = renderIssuesRow({ issueStatus: [{ issue_id: "FOO-43", connection_error: "Oops" }] })
    expect(screen.queryAllByText(/Connection error/).length).toBe(1)
    expect(screen.queryAllByText(/Oops/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows a parse error", async () => {
    const { container } = renderIssuesRow({ issueStatus: [{ issue_id: "FOO-43", parse_error: "Oops" }] })
    expect(screen.queryAllByText(/Parse error/).length).toBe(1)
    expect(screen.queryAllByText(/Oops/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("creates an issue", async () => {
    window.open = vi.fn()
    fetchServerApi.fetchServerApi.mockResolvedValue({ ok: true, error: "", issue_url: "https://tracker/foo-42" })
    const { container } = renderIssuesRow({ report: reportWithIssueTracker })
    fireEvent.click(screen.getByText(/Create new issue/))
    expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith("post", "metric/metric_uuid/issue/new", {
        metric_url: "http://localhost:3000/#metric_uuid",
    })
    await expectNoAccessibilityViolations(container)
})

it("tries to create an issue", async () => {
    fetchServerApi.fetchServerApi.mockResolvedValue({ ok: false, error: "Dummy", issue_url: "" })
    const { container } = renderIssuesRow({ report: reportWithIssueTracker })
    fireEvent.click(screen.getByText(/Create new issue/))
    expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith("post", "metric/metric_uuid/issue/new", {
        metric_url: "http://localhost:3000/#metric_uuid",
    })
    await expectNoAccessibilityViolations(container)
})

it("disables the create issue button if the user has no permissions", async () => {
    const { container } = renderIssuesRow({ report: reportWithIssueTracker, permissions: [] })
    expect(screen.getByText(/Create new issue/)).toBeDisabled()
    await expectNoAccessibilityViolations(container)
})

it("adds an issue id", async () => {
    fetchServerApi.fetchServerApi.mockResolvedValue({ suggestions: [{ key: "FOO-42", text: "Suggestion" }] })
    const { container } = renderIssuesRow()
    await userEvent.type(screen.getByLabelText(/Issue identifiers/), "FOO-42{Enter}")
    expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith("post", "metric/metric_uuid/attribute/issue_ids", {
        issue_ids: ["FOO-42"],
    })
    await expectNoAccessibilityViolations(container)
})

it("shows issue id suggestions", async () => {
    fetchServerApi.fetchServerApi.mockResolvedValue({ suggestions: [{ key: "FOO-42", text: "Suggestion" }] })
    const { container } = renderIssuesRow({
        report: { issue_tracker: { type: "Jira", parameters: { url: "https://jira" } } },
    })
    await userEvent.type(screen.getByLabelText(/Issue identifiers/), "u")
    expect(screen.queryAllByText(/FOO-42: Suggestion/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows an error message if fetching suggestions fails", async () => {
    fetchServerApi.fetchServerApi.mockRejectedValue(new Error("fetching suggestions failed"))
    const showMessage = vi.spyOn(toast, "showMessage")
    const { container } = renderIssuesRow({
        report: { issue_tracker: { type: "Jira", parameters: { url: "https://jira" } } },
    })
    await userEvent.type(screen.getByLabelText(/Issue identifiers/), "u")
    expect(showMessage).toHaveBeenCalledTimes(1)
    expect(showMessage).toHaveBeenCalledWith(
        "error",
        "Could not fetch issue identifiers",
        "Error: fetching suggestions failed",
    )
    await expectNoAccessibilityViolations(container)
})

it("shows no issue id suggestions without a query", async () => {
    fetchServerApi.fetchServerApi.mockResolvedValue({ suggestions: [{ key: "FOO-42", text: "Suggestion" }] })
    const { container } = renderIssuesRow({
        report: { issue_tracker: { type: "Jira", parameters: { url: "https://jira" } } },
    })
    await userEvent.type(screen.getByRole("combobox"), "s")
    expect(screen.queryAllByText(/FOO-42: Suggestion/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
    await userEvent.clear(screen.getByRole("combobox"))
    expect(screen.queryAllByText(/FOO-42: Suggestion/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})
