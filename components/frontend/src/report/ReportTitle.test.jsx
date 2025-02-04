import { act, fireEvent, render, screen, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"

import { createTestableSettings } from "../__fixtures__/fixtures"
import * as changelog_api from "../api/changelog"
import * as report_api from "../api/report"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectNoAccessibilityViolations } from "../testUtils"
import { ReportTitle } from "./ReportTitle"

jest.mock("../api/changelog.js")
jest.mock("../api/report.js")

beforeEach(() => {
    history.push("?expanded=report_uuid")
    jest.resetAllMocks()
})

report_api.get_report_issue_tracker_options.mockImplementation(() =>
    Promise.resolve({ projects: [], issue_types: [], fields: [], epic_links: [] }),
)

const reload = jest.fn

function renderReportTitle() {
    return render(
        <DataModel.Provider value={{ sources: { jira: { name: "Jira", issue_tracker: true } } }}>
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <ReportTitle
                    report={{ report_uuid: "report_uuid", title: "Report" }}
                    reload={reload}
                    settings={createTestableSettings()}
                />
            </Permissions.Provider>
        </DataModel.Provider>,
    )
}

it("deletes the report", async () => {
    report_api.delete_report = jest.fn().mockResolvedValue({ ok: true })
    const { container } = renderReportTitle()
    await act(async () => {
        fireEvent.click(screen.getByText(/Delete report/))
    })
    expect(report_api.delete_report).toHaveBeenLastCalledWith("report_uuid", undefined)
    await expectNoAccessibilityViolations(container)
})

it("sets the title", async () => {
    const { container } = renderReportTitle()
    await userEvent.type(screen.getByLabelText(/Report title/), "New title{Enter}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 12,
    })
    expect(report_api.set_report_attribute).toHaveBeenLastCalledWith("report_uuid", "title", "New title", reload)
    await expectNoAccessibilityViolations(container)
})

it("sets the subtitle", async () => {
    const { container } = renderReportTitle()
    await userEvent.type(screen.getByLabelText(/Report subtitle/), "New subtitle{Enter}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 12,
    })
    expect(report_api.set_report_attribute).toHaveBeenLastCalledWith("report_uuid", "subtitle", "New subtitle", reload)
    await expectNoAccessibilityViolations(container)
})

it("sets the comment", async () => {
    const { container } = renderReportTitle()
    await userEvent.type(screen.getByLabelText(/Comment/), "New comment{Shift>}{Enter}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 8,
    })
    expect(report_api.set_report_attribute).toHaveBeenLastCalledWith("report_uuid", "comment", "New comment", reload)
    await expectNoAccessibilityViolations(container)
})

it("sets the unknown status reaction time", async () => {
    const { container } = renderReportTitle()
    await act(async () => {
        fireEvent.click(screen.getByRole("tab", { name: /reaction times/ }))
    })
    await act(async () => {
        fireEvent.click(screen.getByLabelText("Unknown"))
    })
    await userEvent.type(screen.getByLabelText("Unknown"), "4{Enter}}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 1,
    })
    expect(report_api.set_report_attribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "desired_response_times",
        { unknown: 4 },
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the target not met status reaction time", async () => {
    const { container } = renderReportTitle()
    await act(async () => {
        fireEvent.click(screen.getByText(/reaction times/))
    })
    await userEvent.type(screen.getByLabelText("Target not met"), "5{Enter}}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 1,
    })
    expect(report_api.set_report_attribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "desired_response_times",
        { target_not_met: 5 },
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the near target met status reaction time", async () => {
    const { container } = renderReportTitle()
    await act(async () => {
        fireEvent.click(screen.getByText(/reaction times/))
    })
    await userEvent.type(screen.getByLabelText("Near target met"), "6{Enter}}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 2,
    })
    expect(report_api.set_report_attribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "desired_response_times",
        { near_target_met: 6 },
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the tech debt target status reaction time", async () => {
    const { container } = renderReportTitle()
    await act(async () => {
        fireEvent.click(screen.getByText(/reaction times/))
    })
    await userEvent.type(screen.getByLabelText(/Technical debt target met/), "6{Enter}}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 2,
    })
    expect(report_api.set_report_attribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "desired_response_times",
        { debt_target_met: 6 },
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the confirmed measurement entity status reaction time", async () => {
    const { container } = renderReportTitle()
    await act(async () => {
        fireEvent.click(screen.getByText(/reaction times/))
    })
    await userEvent.type(screen.getByLabelText("Confirmed"), "60{Enter}}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 3,
    })
    expect(report_api.set_report_attribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "desired_response_times",
        { confirmed: 60 },
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the false positive measurement entity status reaction time", async () => {
    const { container } = renderReportTitle()
    await act(async () => {
        fireEvent.click(screen.getByText(/reaction times/))
    })
    await userEvent.type(screen.getByLabelText("False positive"), "70{Enter}}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 3,
    })
    expect(report_api.set_report_attribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "desired_response_times",
        { false_positive: 70 },
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the fixed measurement entity status reaction time", async () => {
    const { container } = renderReportTitle()
    await act(async () => {
        fireEvent.click(screen.getByText(/reaction times/))
    })
    await userEvent.type(screen.getByLabelText("Fixed"), "80{Enter}}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 3,
    })
    expect(report_api.set_report_attribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "desired_response_times",
        { fixed: 80 },
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the won't fixed measurement entity status reaction time", async () => {
    const { container } = renderReportTitle()
    await act(async () => {
        fireEvent.click(screen.getByText(/reaction times/))
    })
    await userEvent.type(screen.getByLabelText("Won't fix"), "90{Enter}}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 3,
    })
    expect(report_api.set_report_attribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "desired_response_times",
        { wont_fix: 90 },
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the issue tracker type", async () => {
    report_api.get_report_issue_tracker_options.mockImplementation(() =>
        Promise.resolve({ projects: [], issue_types: [], fields: [], epic_links: [] }),
    )
    const { container } = renderReportTitle()
    fireEvent.click(screen.getByText(/Issue tracker/))
    fireEvent.mouseDown(screen.getByLabelText(/Issue tracker type/))
    const listbox = within(screen.getByRole("listbox"))
    await act(async () => fireEvent.click(listbox.getByText(/Jira/)))
    expect(report_api.set_report_issue_tracker_attribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "type",
        "jira",
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the issue tracker url", async () => {
    report_api.get_report_issue_tracker_options.mockImplementation(() =>
        Promise.resolve({ projects: [], issue_types: [], fields: [], epic_links: [] }),
    )
    const { container } = renderReportTitle()
    fireEvent.click(screen.getByText(/Issue tracker/))
    await userEvent.type(screen.getByLabelText(/URL/), "https://jira{Enter}")
    expect(report_api.set_report_issue_tracker_attribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "url",
        "https://jira",
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the issue tracker username", async () => {
    report_api.get_report_issue_tracker_options.mockImplementation(() =>
        Promise.resolve({ projects: [], issue_types: [], fields: [], epic_links: [] }),
    )
    const { container } = renderReportTitle()
    fireEvent.click(screen.getByText(/Issue tracker/))
    await userEvent.type(screen.getByLabelText(/Username/), "janedoe{Enter}")
    expect(report_api.set_report_issue_tracker_attribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "username",
        "janedoe",
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the issue tracker password", async () => {
    report_api.get_report_issue_tracker_options.mockImplementation(() =>
        Promise.resolve({ projects: [], issue_types: [], fields: [], epic_links: [] }),
    )
    const { container } = renderReportTitle()
    fireEvent.click(screen.getByText(/Issue tracker/))
    await userEvent.type(screen.getByLabelText(/Password/), "secret{Enter}")
    expect(report_api.set_report_issue_tracker_attribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "password",
        "secret",
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("sets the issue tracker private token", async () => {
    report_api.get_report_issue_tracker_options.mockImplementation(() =>
        Promise.resolve({ projects: [], issue_types: [], fields: [], epic_links: [] }),
    )
    const { container } = renderReportTitle()
    fireEvent.click(screen.getByText(/Issue tracker/))
    await userEvent.type(screen.getByLabelText(/Private token/), "secret{Enter}")
    expect(report_api.set_report_issue_tracker_attribute).toHaveBeenLastCalledWith(
        "report_uuid",
        "private_token",
        "secret",
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("loads the changelog", async () => {
    changelog_api.get_changelog.mockImplementation(() => Promise.resolve({ changelog: [] }))
    const { container } = renderReportTitle()
    await act(async () => {
        fireEvent.click(screen.getByText(/Changelog/))
    })
    expect(changelog_api.get_changelog).toHaveBeenCalledWith(5, { report_uuid: "report_uuid" })
    await expectNoAccessibilityViolations(container)
})

it("shows the notification destinations", async () => {
    const { container } = renderReportTitle()
    fireEvent.click(screen.getByText(/Notifications/))
    expect(screen.getAllByText(/No notification destinations/).length).toBe(2)
    await expectNoAccessibilityViolations(container)
})
