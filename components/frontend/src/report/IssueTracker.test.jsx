import { act, fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as reportApi from "../api/report"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectNoAccessibilityViolations } from "../testUtils"
import { IssueTracker } from "./IssueTracker"

beforeEach(() => {
    vi.spyOn(reportApi, "setReportIssueTrackerAttribute")
    vi.spyOn(reportApi, "getReportIssueTrackerOptions").mockImplementation(() =>
        Promise.resolve({
            projects: [{ key: "PRJ", name: "Project name" }],
            issue_types: [{ key: "Bug", name: "Bug" }],
            fields: [{ key: "labels", name: "Labels" }],
            epic_links: [{ key: "FOO-420", name: "FOO-420" }],
        }),
    )
})

const reload = vi.fn()

async function renderIssueTracker({ report = { report_uuid: "report_uuid", title: "Report" }, helpUrl = "" } = {}) {
    let result
    await act(async () => {
        result = render(
            <DataModel.Provider
                value={{
                    sources: {
                        jira: {
                            name: "Jira",
                            issue_tracker: true,
                            parameters: { private_token: { help_url: helpUrl } },
                        },
                    },
                }}
            >
                <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                    <IssueTracker report={report} reload={reload} />
                </Permissions.Provider>
            </DataModel.Provider>,
        )
    })
    return result
}

it("sets the issue tracker type", async () => {
    const { container } = await renderIssueTracker()
    fireEvent.mouseDown(screen.getByLabelText(/Issue tracker type/))
    fireEvent.click(screen.getByText("Jira"))
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith("report_uuid", "type", "jira", reload)
    await expectNoAccessibilityViolations(container)
})

it("sets the issue tracker url", async () => {
    const { container } = await renderIssueTracker()
    await userEvent.type(screen.getByLabelText(/URL/), "https://jira{Enter}")
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "url",
        "https://jira",
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the issue tracker username", async () => {
    const { container } = await renderIssueTracker()
    await userEvent.type(screen.getByLabelText(/Username/), "janedoe{Enter}")
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "username",
        "janedoe",
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the issue tracker password", async () => {
    const { container } = await renderIssueTracker()
    await userEvent.type(screen.getByLabelText(/Password/), "secret{Enter}")
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "password",
        "secret",
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the issue tracker private token", async () => {
    const { container } = await renderIssueTracker()
    await userEvent.type(screen.getByLabelText(/Private token/), "secret{Enter}")
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "private_token",
        "secret",
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("does not show the issue tracker private token help url if there is no issue tracker", async () => {
    const { container } = await renderIssueTracker({
        report: { report_uuid: "report_uuid", title: "Report", issue_tracker: {} },
        helpUrl: "https://help",
    })
    expect(container.querySelector("a")).toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("does not show the issue tracker private token help url if the data model has no help url", async () => {
    const { container } = await renderIssueTracker({
        report_uuid: "report_uuid",
        title: "Report",
        issue_tracker: { type: "jira" },
    })
    expect(container.querySelector("a")).toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("shows the issue tracker private token help url", async () => {
    const { container } = await renderIssueTracker({
        report: {
            report_uuid: "report_uuid",
            title: "Report",
            issue_tracker: { type: "jira" },
        },
        helpUrl: "https://help",
    })
    expect(container.querySelector("a")).toHaveAttribute("href", "https://help")
    await expectNoAccessibilityViolations(container)
})

it("sets the issue tracker project", async () => {
    const { container } = await renderIssueTracker()
    fireEvent.mouseDown(screen.getByLabelText(/Project for new issues/))
    fireEvent.click(screen.getByText(/Project name/))
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "project_key",
        "PRJ",
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the issue tracker issue type", async () => {
    const { container } = await renderIssueTracker()
    fireEvent.mouseDown(screen.getByLabelText(/Issue type/))
    fireEvent.click(screen.getByText(/Bug/))
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "issue_type",
        "Bug",
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the issue tracker issue labels", async () => {
    const { container } = await renderIssueTracker()
    await userEvent.type(screen.getByLabelText(/Labels/), "Label{Enter}")
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "issue_labels",
        ["Label"],
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the issue tracker epic link", async () => {
    const { container } = await renderIssueTracker()
    fireEvent.mouseDown(screen.getByLabelText(/Epic link/))
    fireEvent.click(screen.getByText(/FOO-420/))
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "epic_link",
        "FOO-420",
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("does not show the issue labels warning without tracker project", async () => {
    const { container } = await renderIssueTracker({
        report: {
            report_uuid: "report_uuid",
            title: "Report",
            issue_tracker: { type: "jira" },
        },
    })
    expect(screen.queryAllByText(/Labels not supported/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("does not show the issue labels warning without issue type", async () => {
    const { container } = await renderIssueTracker({
        report: {
            report_uuid: "report_uuid",
            title: "Report",
            issue_tracker: { type: "jira", parameters: { project_key: "PRJ" } },
        },
    })
    expect(screen.queryAllByText(/Labels not supported/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("does not show the issue labels warning with issue type that supports labels", async () => {
    const { container } = await renderIssueTracker({
        report: {
            report_uuid: "report_uuid",
            title: "Report",
            issue_tracker: {
                type: "jira",
                parameters: { project_key: "PRJ", issue_type: "Bug" },
            },
        },
    })
    expect(screen.queryAllByText(/Labels not supported/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("does show the issue labels warning with issue type that does not support labels", async () => {
    reportApi.getReportIssueTrackerOptions.mockImplementation(() =>
        Promise.resolve({
            projects: [{ key: "PRJ", name: "Project name" }],
            issue_types: [{ key: "Bug", name: "Bug" }],
            fields: [],
            epic_links: [],
        }),
    )
    const { container } = await renderIssueTracker({
        report: {
            report_uuid: "report_uuid",
            title: "Report",
            issue_tracker: {
                type: "jira",
                parameters: { project_key: "PRJ", issue_type: "Bug" },
            },
        },
    })
    expect(screen.queryAllByText(/Labels not supported/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})
