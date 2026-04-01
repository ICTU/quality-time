import { act, fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as reportApi from "../api/report"
import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import { clickText, expectNoAccessibilityViolations, expectNoText, expectText } from "../testUtils"
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
            <DataModelContext
                value={{
                    sources: {
                        jira: {
                            name: "Jira",
                            issue_tracker: true,
                            parameters: {
                                private_token: { help_url: helpUrl },
                                api_version: { default_value: "v2", values: ["v2", "v3"] },
                            },
                        },
                    },
                }}
            >
                <PermissionsContext value={[EDIT_REPORT_PERMISSION]}>
                    <IssueTracker report={report} reload={reload} />
                </PermissionsContext>
            </DataModelContext>,
        )
    })
    return result
}

const reportWithIssueTracker = {
    report_uuid: "report_uuid",
    title: "Report",
    issue_tracker: { type: "jira" },
}

it("has no accessibility violations", async () => {
    const { container } = await renderIssueTracker()
    await expectNoAccessibilityViolations(container)
})

it("sets the issue tracker type", async () => {
    await renderIssueTracker()
    fireEvent.mouseDown(screen.getByLabelText(/Issue tracker type/))
    clickText("Jira")
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith("report_uuid", "type", "jira", reload)
    fireEvent.click(screen.getByText("None"))
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith("report_uuid", "type", "", reload)
})

function expectIssueTrackerFieldsToBeDisabled() {
    const textFields = [/URL/, /Username/, /Password/, /Private token/, /API version/, /Labels for new issues/]
    textFields.forEach((field) => expect(screen.getByLabelText(field)).toBeDisabled())
    const selectionFields = [/Project for new issues/, /Issue type/, /Epic link/]
    selectionFields.forEach((field) => expect(screen.getByLabelText(field).nextSibling).toBeDisabled())
}

it("cannot edit issue tracker fields without picking an issue tracker type", async () => {
    await renderIssueTracker()
    expectIssueTrackerFieldsToBeDisabled()
})

it("cannot edit issue tracker fields if the issue tracker type is None", async () => {
    await renderIssueTracker({
        report_uuid: "report_uuid",
        title: "Report",
        issue_tracker: { type: "None" },
    })
    expectIssueTrackerFieldsToBeDisabled()
})

it("sets the issue tracker url", async () => {
    await renderIssueTracker({ report: reportWithIssueTracker })
    await userEvent.type(screen.getByLabelText(/URL/), "https://jira.example.org{Enter}")
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "url",
        "https://jira.example.org",
        reload,
    )
})

it("sets the issue tracker username", async () => {
    await renderIssueTracker({ report: reportWithIssueTracker })
    expect(screen.getByLabelText(/Username/)).not.toBeDisabled()
    await userEvent.type(screen.getByLabelText(/Username/), "janedoe{Enter}")
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "username",
        "janedoe",
        reload,
    )
})

it("sets the issue tracker password", async () => {
    await renderIssueTracker({ report: reportWithIssueTracker })
    await userEvent.type(screen.getByLabelText(/Password/), "secret{Enter}")
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "password",
        "secret",
        reload,
    )
})

it("sets the issue tracker private token", async () => {
    await renderIssueTracker({ report: reportWithIssueTracker })
    await userEvent.type(screen.getByLabelText(/Private token/), "secret{Enter}")
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "private_token",
        "secret",
        reload,
    )
})

it("does not show the issue tracker private token help url if there is no issue tracker", async () => {
    const { container } = await renderIssueTracker({
        report: { report_uuid: "report_uuid", title: "Report", issue_tracker: {} },
        helpUrl: "https://help.example.org",
    })
    expect(container.querySelector("a")).toBe(null)
})

it("does not show the issue tracker private token help url if the data model has no help url", async () => {
    const { container } = await renderIssueTracker()
    expect(container.querySelector("a")).toBe(null)
})

it("shows the issue tracker private token help url", async () => {
    const { container } = await renderIssueTracker({
        report: reportWithIssueTracker,
        helpUrl: "https://help.example.org",
    })
    expect(container.querySelector("a")).toHaveAttribute("href", "https://help.example.org")
})

it("sets the issue tracker API version", async () => {
    await renderIssueTracker({ report: reportWithIssueTracker })
    fireEvent.mouseDown(screen.getByLabelText(/API version/))
    clickText(/v3/)
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "api_version",
        "v3",
        reload,
    )
})

it("sets the issue tracker project", async () => {
    await renderIssueTracker({ report: reportWithIssueTracker, helpUrl: "https://help" })
    fireEvent.mouseDown(screen.getByLabelText(/Project for new issues/))
    clickText(/Project name/)
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "project_key",
        "PRJ",
        reload,
    )
})

it("sets the issue tracker issue type", async () => {
    await renderIssueTracker({ report: reportWithIssueTracker, helpUrl: "https://help" })
    fireEvent.mouseDown(screen.getByLabelText(/Issue type/))
    clickText(/Bug/)
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "issue_type",
        "Bug",
        reload,
    )
})

it("sets the issue tracker issue labels", async () => {
    await renderIssueTracker({ report: reportWithIssueTracker, helpUrl: "https://help" })
    await userEvent.type(screen.getByLabelText(/Labels/), "Label{Enter}")
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "issue_labels",
        ["Label"],
        reload,
    )
})

it("sets the issue tracker epic link", async () => {
    await renderIssueTracker({ report: reportWithIssueTracker, helpUrl: "https://help" })
    fireEvent.mouseDown(screen.getByLabelText(/Epic link/))
    clickText(/FOO-420/)
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "epic_link",
        "FOO-420",
        reload,
    )
})

it("does not show the issue labels warning without tracker project", async () => {
    await renderIssueTracker({ report: reportWithIssueTracker })
    expectNoText(/Labels not supported/)
})

it("does not show the issue labels warning without issue type", async () => {
    await renderIssueTracker({
        report: {
            report_uuid: "report_uuid",
            title: "Report",
            issue_tracker: { type: "jira", parameters: { project_key: "PRJ" } },
        },
    })
    expectNoText(/Labels not supported/)
})

it("does not show the issue labels warning with issue type that supports labels", async () => {
    await renderIssueTracker({
        report: {
            report_uuid: "report_uuid",
            title: "Report",
            issue_tracker: {
                type: "jira",
                parameters: { project_key: "PRJ", issue_type: "Bug" },
            },
        },
    })
    expectNoText(/Labels not supported/)
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
    await renderIssueTracker({
        report: {
            report_uuid: "report_uuid",
            title: "Report",
            issue_tracker: {
                type: "jira",
                parameters: { project_key: "PRJ", issue_type: "Bug" },
            },
        },
    })
    expectText(/Labels not supported/)
})
