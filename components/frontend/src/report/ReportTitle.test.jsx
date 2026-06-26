import { act, fireEvent, render, screen, within } from "@testing-library/react"
import history from "history/browser"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { useSettings } from "../app_ui_settings"
import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import {
    asyncClickLabeledElement,
    asyncClickText,
    enterLabeledText,
    expectFetch,
    expectNoAccessibilityViolations,
    expectNoText,
    expectSearch,
    expectText,
    mouseDownLabeledElement,
    typeLabeledText,
} from "../testUtils"
import { SnackbarAlerts } from "../widgets/SnackbarAlerts"
import { ReportTitle } from "./ReportTitle"

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true })
})

const reportDates = [new Date()]

function ReportTitleWrapper({ issueTrackerType, permissions, tags }) {
    const settings = useSettings()
    return (
        <DataModelContext value={{ sources: { jira: { name: "Jira", issue_tracker: true } } }}>
            <PermissionsContext value={permissions}>
                <SnackbarAlerts messages={[]} showMessage={vi.fn()}>
                    <ReportTitle
                        dates={reportDates}
                        measurements={[]}
                        report={{
                            issue_tracker: { type: issueTrackerType },
                            report_uuid: "report_uuid",
                            title: "Report",
                            subjects: { subject_uuid: { metrics: { metric_uuid: { tags: tags } } } },
                        }}
                        reload={vi.fn()}
                        settings={settings}
                    />
                </SnackbarAlerts>
            </PermissionsContext>
        </DataModelContext>
    )
}

function renderReportTitle({ tags = ["foo"], issueTrackerType = null, permissions = [EDIT_REPORT_PERMISSION] } = {}) {
    return render(<ReportTitleWrapper issueTrackerType={issueTrackerType} permissions={permissions} tags={tags} />)
}

it("shows the export report button", async () => {
    history.push("?expanded=report_uuid:0")
    const { container } = renderReportTitle()
    expectText(/Export as JSON/)
    await expectNoAccessibilityViolations(container)
})

it("shows the export as CSV button to all users", async () => {
    history.push("?expanded=report_uuid:0")
    const { container } = renderReportTitle({ permissions: [] })
    expectText(/Export as CSV/)
    expectNoText(/Export as JSON/)
    await expectNoAccessibilityViolations(container)
})

it("deletes the report", async () => {
    history.push("?expanded=report_uuid:0")
    const { container } = renderReportTitle()
    await asyncClickText(/Delete report/)
    expectFetch("delete", "report/report_uuid", {})
    expectSearch("")
    await expectNoAccessibilityViolations(container)
})

describe("configuration tab", () => {
    beforeEach(() => history.push("?expanded=report_uuid:0"))

    it("has no accessibility violations", async () => {
        const { container } = renderReportTitle()
        await expectNoAccessibilityViolations(container)
    })

    it("sets the title", async () => {
        renderReportTitle()
        await enterLabeledText(/Report title/, "New title", {
            initialSelectionStart: 0,
            initialSelectionEnd: 12,
        })
        expectFetch("post", "report/report_uuid/attribute/title", { title: "New title" })
    })

    it("sets the subtitle", async () => {
        renderReportTitle()
        await enterLabeledText(/Report subtitle/, "New subtitle", {
            initialSelectionStart: 0,
            initialSelectionEnd: 12,
        })
        expectFetch("post", "report/report_uuid/attribute/subtitle", { subtitle: "New subtitle" })
    })

    it("sets the comment", async () => {
        renderReportTitle()
        await typeLabeledText(/Comment/, "New comment{Shift>}{Enter}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 8,
        })
        expectFetch("post", "report/report_uuid/attribute/comment", { comment: "New comment" })
    })
})

describe("desired reaction times tab", () => {
    beforeEach(() => history.push("?expanded=report_uuid:1"))

    it("has no accessibility violations", async () => {
        const { container } = renderReportTitle()
        await expectNoAccessibilityViolations(container)
    })

    it("sets the unknown status reaction time", async () => {
        renderReportTitle()
        await asyncClickLabeledElement("Unknown")
        await typeLabeledText("Unknown", "4{Enter}}", { initialSelectionStart: 0, initialSelectionEnd: 1 })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { unknown: 4 },
        })
    })

    it("sets the target not met status reaction time", async () => {
        renderReportTitle()
        await typeLabeledText("Target not met", "5{Enter}}", { initialSelectionStart: 0, initialSelectionEnd: 1 })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { target_not_met: 5 },
        })
    })

    it("sets the near target met status reaction time", async () => {
        renderReportTitle()
        await typeLabeledText("Near target met", "6{Enter}}", { initialSelectionStart: 0, initialSelectionEnd: 2 })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { near_target_met: 6 },
        })
    })

    it("sets the tech debt target status reaction time", async () => {
        renderReportTitle()
        await typeLabeledText(/Technical debt target met/, "6{Enter}}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 2,
        })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { debt_target_met: 6 },
        })
    })

    it("sets the confirmed measurement entity status reaction time", async () => {
        renderReportTitle()
        await typeLabeledText("Confirmed", "60{Enter}}", { initialSelectionStart: 0, initialSelectionEnd: 3 })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { confirmed: 60 },
        })
    })

    it("sets the false positive measurement entity status reaction time", async () => {
        renderReportTitle()
        await typeLabeledText("False positive", "70{Enter}}", { initialSelectionStart: 0, initialSelectionEnd: 3 })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { false_positive: 70 },
        })
    })

    it("sets the fixed measurement entity status reaction time", async () => {
        renderReportTitle()
        await typeLabeledText("Fixed", "80{Enter}}", { initialSelectionStart: 0, initialSelectionEnd: 3 })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { fixed: 80 },
        })
    })

    it("sets the won't fixed measurement entity status reaction time", async () => {
        renderReportTitle()
        await typeLabeledText("Won't fix", "90{Enter}}", { initialSelectionStart: 0, initialSelectionEnd: 3 })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { wont_fix: 90 },
        })
    })
})

describe("notification destinations tab", () => {
    beforeEach(() => history.push("?expanded=report_uuid:2"))

    it("has no accessibility violations", async () => {
        const { container } = renderReportTitle()
        await expectNoAccessibilityViolations(container)
    })

    it("shows the notification destinations", async () => {
        renderReportTitle()
        expectText(/No notification destinations/, 2)
    })
})

describe("issue tracker tab", () => {
    beforeEach(() => history.push("?expanded=report_uuid:3"))

    it("has no accessibility violations", async () => {
        const { container } = renderReportTitle()
        await expectNoAccessibilityViolations(container)
    })

    it("sets the issue tracker type", async () => {
        fetchServerApi.fetchServerApi.mockImplementation(() =>
            Promise.resolve({ projects: [], issue_types: [], fields: [], epic_links: [] }),
        )
        renderReportTitle()
        mouseDownLabeledElement(/Issue tracker type/)
        const listbox = within(screen.getByRole("listbox"))
        await act(async () => fireEvent.click(listbox.getByText(/Jira/)))
        expectFetch("post", "report/report_uuid/issue_tracker/type", { type: "jira" })
    })

    it("sets the issue tracker url", async () => {
        renderReportTitle({ issueTrackerType: "jira" })
        await enterLabeledText(/URL/, "https://jira")
        expectFetch("post", "report/report_uuid/issue_tracker/url", { url: "https://jira" })
    })

    it("sets the issue tracker username", async () => {
        renderReportTitle({ issueTrackerType: "jira" })
        await enterLabeledText(/Username/, "janedoe")
        expectFetch("post", "report/report_uuid/issue_tracker/username", { username: "janedoe" })
    })

    it("sets the issue tracker password", async () => {
        renderReportTitle({ issueTrackerType: "jira" })
        await enterLabeledText(/Password/, "secret")
        expectFetch("post", "report/report_uuid/issue_tracker/password", { password: "secret" })
    })

    it("sets the issue tracker private token", async () => {
        renderReportTitle({ issueTrackerType: "jira" })
        await enterLabeledText(/Private token/, "secret")
        expectFetch("post", "report/report_uuid/issue_tracker/private_token", { private_token: "secret" })
    })
})

describe("sources tab", () => {
    beforeEach(() => history.push("?expanded=report_uuid:4"))

    it("has no accessibility violations", async () => {
        const { container } = renderReportTitle()
        await expectNoAccessibilityViolations(container)
    })

    it("shows the sources, if available", async () => {
        renderReportTitle()
        expectText(/No sources have been configured yet/)
    })
})

describe("tags tab", () => {
    beforeEach(() => history.push("?expanded=report_uuid:5"))

    it("has no accessibility violations", async () => {
        const { container } = renderReportTitle()
        await expectNoAccessibilityViolations(container)
    })

    it("shows the tags", async () => {
        renderReportTitle()
        expectText(/Tags/)
    })
})

describe("changelog tab", () => {
    beforeEach(() => history.push("?expanded=report_uuid:6"))

    it("has no accessibility violations", async () => {
        const { container } = renderReportTitle()
        await expectNoAccessibilityViolations(container)
    })

    it("loads the changelog", async () => {
        fetchServerApi.fetchServerApi.mockImplementation(() => Promise.resolve({ changelog: [] }))
        renderReportTitle()
        await act(async () => expectFetch("get", "changelog/report/report_uuid/5"))
    })
})
