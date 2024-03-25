import { fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import * as fetch_server_api from "../api/fetch_server_api"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { IssuesRows } from "./IssuesRows"

jest.mock("../api/fetch_server_api.js")

const reportWithIssueTracker = {
    issue_tracker: {
        type: "Jira",
        parameters: { url: "https://jira", project_key: "KEY", issue_type: "Bug" },
    },
}

function renderIssuesRow({
    issue_ids = [],
    report = { subjects: {} },
    permissions = [EDIT_REPORT_PERMISSION],
    issue_status = [],
} = {}) {
    render(
        <Permissions.Provider value={permissions}>
            <IssuesRows
                metric={{
                    type: "violations",
                    issue_ids: issue_ids,
                    issue_status: issue_status,
                }}
                metric_uuid="metric_uuid"
                reload={jest.fn}
                report={report}
            />
        </Permissions.Provider>,
    )
}

it("does not show an error message if the metric has no issues and no issue tracker is configured", () => {
    renderIssuesRow()
    expect(screen.queryAllByText(/No issue tracker configured/).length).toBe(0)
})

it("does not show an error message if the metric has no issues and an issue tracker is configured", () => {
    renderIssuesRow({ report: { issue_tracker: { type: "Jira" } } })
    expect(screen.queryAllByText(/No issue tracker configured/).length).toBe(0)
})

it("does not show an error message if the metric has issues and an issue tracker is configured", () => {
    renderIssuesRow({
        issue_ids: ["BAR-42"],
        report: {
            issue_tracker: {
                type: "Jira",
                parameters: { url: "https://jira", project_key: "KEY", issue_type: "Bug" },
            },
        },
    })
    expect(screen.queryAllByText(/No issue tracker configured/).length).toBe(0)
})

it("shows an error message if the metric has issues but no issue tracker is configured", () => {
    renderIssuesRow({ issue_ids: ["FOO-42"] })
    expect(screen.queryAllByText(/No issue tracker configured/).length).toBe(1)
})

it("shows a connection error", () => {
    renderIssuesRow({ issue_status: [{ issue_id: "FOO-43", connection_error: "Oops" }] })
    expect(screen.queryAllByText(/Connection error/).length).toBe(1)
    expect(screen.queryAllByText(/Oops/).length).toBe(1)
})

it("shows a parse error", () => {
    renderIssuesRow({ issue_status: [{ issue_id: "FOO-43", parse_error: "Oops" }] })
    expect(screen.queryAllByText(/Parse error/).length).toBe(1)
    expect(screen.queryAllByText(/Oops/).length).toBe(1)
})

it("creates an issue", () => {
    window.open = jest.fn()
    fetch_server_api.fetch_server_api = jest
        .fn()
        .mockResolvedValue({ ok: true, error: "", issue_url: "https://tracker/foo-42" })
    renderIssuesRow({ report: reportWithIssueTracker })
    fireEvent.click(screen.getByText(/Create new issue/))
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/issue/new", {
        metric_url: "http://localhost/#metric_uuid",
    })
})

it("tries to create an issue", () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: false, error: "Dummy", issue_url: "" })
    renderIssuesRow({ report: reportWithIssueTracker })
    fireEvent.click(screen.getByText(/Create new issue/))
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/issue/new", {
        metric_url: "http://localhost/#metric_uuid",
    })
})

it("does not show the create issue button if the user has no permissions", () => {
    renderIssuesRow({ report: reportWithIssueTracker, permissions: [] })
    expect(screen.queryAllByText(/Create new issue/).length).toBe(0)
})

it("adds an issue id", async () => {
    fetch_server_api.fetch_server_api = jest
        .fn()
        .mockResolvedValue({ suggestions: [{ key: "FOO-42", text: "Suggestion" }] })
    renderIssuesRow()
    await userEvent.type(screen.getByLabelText(/Issue identifiers/), "FOO-42{Enter}")
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith(
        "post",
        "metric/metric_uuid/attribute/issue_ids",
        { issue_ids: ["FOO-42"] },
    )
})

it("shows issue id suggestions", async () => {
    fetch_server_api.fetch_server_api = jest
        .fn()
        .mockResolvedValue({ suggestions: [{ key: "FOO-42", text: "Suggestion" }] })
    renderIssuesRow({
        report: { issue_tracker: { type: "Jira", parameters: { url: "https://jira" } } },
    })
    await userEvent.type(screen.getByLabelText(/Issue identifiers/), "u")
    expect(screen.queryAllByText(/FOO-42: Suggestion/).length).toBe(1)
})

it("shows no issue id suggestions without a query", async () => {
    fetch_server_api.fetch_server_api = jest
        .fn()
        .mockResolvedValue({ suggestions: [{ key: "FOO-42", text: "Suggestion" }] })
    renderIssuesRow({
        report: { issue_tracker: { type: "Jira", parameters: { url: "https://jira" } } },
    })
    await userEvent.type(screen.getByLabelText(/Issue identifiers/), "s")
    expect(screen.queryAllByText(/FOO-42: Suggestion/).length).toBe(1)
    await userEvent.clear(screen.getByLabelText(/Issue identifiers/).firstChild)
    expect(screen.queryAllByText(/FOO-42: Suggestion/).length).toBe(0)
})
