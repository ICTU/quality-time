import { act, fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as reportApi from "../api/report"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
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
            <DataModel.Provider
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
                <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                    <IssueTracker report={report} reload={reload} />
                </Permissions.Provider>
            </DataModel.Provider>,
        )
    })
    return result
}

const reportWithIssueTracker = {
    report_uuid: "report_uuid",
    title: "Report",
    issue_tracker: { type: "jira" },
}

it("sets the issue tracker type", async () => {
    const { container } = await renderIssueTracker()
    fireEvent.mouseDown(screen.getByLabelText(/Issue tracker type/))
    clickText("Jira")
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith("report_uuid", "type", "jira", reload)
    fireEvent.click(screen.getByText("None"))
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith("report_uuid", "type", "", reload)
    await expectNoAccessibilityViolations(container)
})

function expectIssueTrackerFieldsToBeDisabled() {
    const textFields = [/URL/, /Username/, /Password/, /Private token/, /API version/, /Labels for new issues/]
    textFields.forEach((field) => expect(screen.getByLabelText(field)).toBeDisabled())
    const selectionFields = [/Project for new issues/, /Issue type/, /Epic link/]
    selectionFields.forEach((field) => expect(screen.getByLabelText(field).nextSibling).toBeDisabled())
}

it("cannot edit issue tracker fields without picking an issue tracker type", async () => {
    const { container } = await renderIssueTracker()
    expectIssueTrackerFieldsToBeDisabled()
    await expectNoAccessibilityViolations(container)
})

it("cannot edit issue tracker fields if the issue tracker type is None", async () => {
    const { container } = await renderIssueTracker({
        report_uuid: "report_uuid",
        title: "Report",
        issue_tracker: { type: "None" },
    })
    expectIssueTrackerFieldsToBeDisabled()
    await expectNoAccessibilityViolations(container)
})

it("sets the issue tracker url", async () => {
    const { container } = await renderIssueTracker({ report: reportWithIssueTracker })
    await userEvent.type(screen.getByLabelText(/URL/), "https://jira.example.org{Enter}")
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "url",
        "https://jira.example.org",
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the issue tracker username", async () => {
    const { container } = await renderIssueTracker({ report: reportWithIssueTracker })
    expect(screen.getByLabelText(/Username/)).not.toBeDisabled()
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
    const { container } = await renderIssueTracker({ report: reportWithIssueTracker })
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
    const { container } = await renderIssueTracker({ report: reportWithIssueTracker })
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
        helpUrl: "https://help.example.org",
    })
    expect(container.querySelector("a")).toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("does not show the issue tracker private token help url if the data model has no help url", async () => {
    const { container } = await renderIssueTracker()
    expect(container.querySelector("a")).toBe(null)
    await expectNoAccessibilityViolations(container)
})

it("shows the issue tracker private token help url", async () => {
    const { container } = await renderIssueTracker({
        report: reportWithIssueTracker,
        helpUrl: "https://help.example.org",
    })
    expect(container.querySelector("a")).toHaveAttribute("href", "https://help.example.org")
    await expectNoAccessibilityViolations(container)
})

it("sets the issue tracker API version", async () => {
    const { container } = await renderIssueTracker({ report: reportWithIssueTracker })
    fireEvent.mouseDown(screen.getByLabelText(/API version/))
    clickText(/v3/)
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "api_version",
        "v3",
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the issue tracker project", async () => {
    const { container } = await renderIssueTracker({ report: reportWithIssueTracker, helpUrl: "https://help" })
    fireEvent.mouseDown(screen.getByLabelText(/Project for new issues/))
    clickText(/Project name/)
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "project_key",
        "PRJ",
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the issue tracker issue type", async () => {
    const { container } = await renderIssueTracker({ report: reportWithIssueTracker, helpUrl: "https://help" })
    fireEvent.mouseDown(screen.getByLabelText(/Issue type/))
    clickText(/Bug/)
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "issue_type",
        "Bug",
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the issue tracker issue labels", async () => {
    const { container } = await renderIssueTracker({ report: reportWithIssueTracker, helpUrl: "https://help" })
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
    const { container } = await renderIssueTracker({ report: reportWithIssueTracker, helpUrl: "https://help" })
    fireEvent.mouseDown(screen.getByLabelText(/Epic link/))
    clickText(/FOO-420/)
    expect(reportApi.setReportIssueTrackerAttribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "epic_link",
        "FOO-420",
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("does not show the issue labels warning without tracker project", async () => {
    const { container } = await renderIssueTracker({ report: reportWithIssueTracker })
    expectNoText(/Labels not supported/)
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
    expectNoText(/Labels not supported/)
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
    expectNoText(/Labels not supported/)
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
    expectText(/Labels not supported/)
    await expectNoAccessibilityViolations(container)
})
