import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import { clickText, expectFetch, expectNoAccessibilityViolations, expectNoText, expectText } from "../testUtils"
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
        <PermissionsContext value={permissions}>
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
        </PermissionsContext>,
    )
}

it("has no accessibility violations", async () => {
    const { container } = renderIssuesRow()
    await expectNoAccessibilityViolations(container)
})

it("does not show an error message if the metric has no issues and no issue tracker is configured", async () => {
    renderIssuesRow()
    expectNoText(/No issue tracker configured/)
})

it("does not show an error message if the metric has no issues and an issue tracker is configured", async () => {
    renderIssuesRow({ report: { issue_tracker: { type: "Jira" } } })
    expectNoText(/No issue tracker configured/)
})

it("does not show an error message if the metric has issues and an issue tracker is configured", async () => {
    renderIssuesRow({
        issueIds: ["BAR-42"],
        report: {
            issue_tracker: {
                type: "Jira",
                parameters: { url: "https://jira", project_key: "KEY", issue_type: "Bug" },
            },
        },
    })
    expectNoText(/No issue tracker configured/)
})

it("shows an error message if the metric has issues but no issue tracker is configured", async () => {
    renderIssuesRow({ issueIds: ["FOO-42"] })
    expectText(/No issue tracker configured/)
})

it("shows a connection error", async () => {
    renderIssuesRow({ issueStatus: [{ issue_id: "FOO-43", connection_error: "Oops" }] })
    expectText(/Connection error/)
    expectText(/Oops/)
})

it("shows a parse error", async () => {
    renderIssuesRow({ issueStatus: [{ issue_id: "FOO-43", parse_error: "Oops" }] })
    expectText(/Parse error/)
    expectText(/Oops/)
})

it("creates an issue", async () => {
    fetchServerApi.fetchServerApi.mockResolvedValue({ ok: true, error: "", issue_url: "https://tracker/foo-42" })
    globalThis.open = vi.fn()
    globalThis.location = {
        origin: "https://quality-time.example.org",
        pathname: "/report_uuid",
        search: "?query=ignored",
    }
    renderIssuesRow({ report: reportWithIssueTracker })
    clickText(/Create new issue/)
    expectFetch("post", "metric/metric_uuid/issue/new", {
        metric_url: "https://quality-time.example.org/report_uuid#metric_uuid",
    })
})

it("tries to create an issue", async () => {
    const showMessage = vi.spyOn(toast, "showMessage")
    fetchServerApi.fetchServerApi.mockResolvedValue({ ok: false, error: "Failed to create issue", issue_url: "" })
    globalThis.location = {
        origin: "https://quality-time.example.org",
        pathname: "/report_uuid",
        search: "?query=ignored",
    }
    renderIssuesRow({ report: reportWithIssueTracker })
    clickText(/Create new issue/)
    expectFetch("post", "metric/metric_uuid/issue/new", {
        metric_url: "https://quality-time.example.org/report_uuid#metric_uuid",
    })
    await waitFor(() => {
        expect(showMessage).toHaveBeenCalledTimes(1)
        expect(showMessage).toHaveBeenCalledWith("error", "Could not create issue", "Failed to create issue")
    })
})

it("disables the create issue button if the user has no permissions", async () => {
    renderIssuesRow({ report: reportWithIssueTracker, permissions: [] })
    expect(screen.getByText(/Create new issue/)).toBeDisabled()
})

it("adds an issue id", async () => {
    fetchServerApi.fetchServerApi.mockResolvedValue({ suggestions: [{ key: "FOO-42", text: "Suggestion" }] })
    renderIssuesRow()
    await userEvent.type(screen.getByLabelText(/Issue identifiers/), "FOO-42{Enter}")
    expectFetch("post", "metric/metric_uuid/attribute/issue_ids", {
        issue_ids: ["FOO-42"],
    })
})

it("shows issue id suggestions", async () => {
    fetchServerApi.fetchServerApi.mockResolvedValue({ suggestions: [{ key: "FOO-42", text: "Suggestion" }] })
    renderIssuesRow({
        report: { issue_tracker: { type: "Jira", parameters: { url: "https://jira" } } },
    })
    await userEvent.type(screen.getByLabelText(/Issue identifiers/), "u")
    expectText(/FOO-42: Suggestion/)
})

it("shows an error message if fetching suggestions fails", async () => {
    fetchServerApi.fetchServerApi.mockRejectedValue(new Error("fetching suggestions failed"))
    const showMessage = vi.spyOn(toast, "showMessage")
    renderIssuesRow({
        report: { issue_tracker: { type: "Jira", parameters: { url: "https://jira" } } },
    })
    await userEvent.type(screen.getByLabelText(/Issue identifiers/), "u")
    expect(showMessage).toHaveBeenCalledTimes(1)
    expect(showMessage).toHaveBeenCalledWith(
        "error",
        "Could not fetch issue identifiers",
        "Error: fetching suggestions failed",
    )
})

it("shows no issue id suggestions without a query", async () => {
    fetchServerApi.fetchServerApi.mockResolvedValue({ suggestions: [{ key: "FOO-42", text: "Suggestion" }] })
    renderIssuesRow({
        report: { issue_tracker: { type: "Jira", parameters: { url: "https://jira" } } },
    })
    await userEvent.type(screen.getByRole("combobox"), "s")
    expectText(/FOO-42: Suggestion/)
    await userEvent.clear(screen.getByRole("combobox"))
    expectNoText(/FOO-42: Suggestion/)
})
