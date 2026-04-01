import { act, fireEvent, render, screen, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings } from "../__fixtures__/fixtures"
import * as fetchServerApi from "../api/fetch_server_api"
import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import {
    asyncClickLabeledElement,
    asyncClickText,
    expectFetch,
    expectNoAccessibilityViolations,
    expectSearch,
    expectText,
} from "../testUtils"
import { ReportTitle } from "./ReportTitle"

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true })
})

function renderReportTitle({ tags = ["foo"], issueTrackerType = null } = {}) {
    return render(
        <DataModelContext value={{ sources: { jira: { name: "Jira", issue_tracker: true } } }}>
            <PermissionsContext value={[EDIT_REPORT_PERMISSION]}>
                <ReportTitle
                    report={{
                        issue_tracker: { type: issueTrackerType },
                        report_uuid: "report_uuid",
                        title: "Report",
                        subjects: { subject_uuid: { metrics: { metric_uuid: { tags: tags } } } },
                    }}
                    reload={vi.fn()}
                    settings={createTestableSettings()}
                />
            </PermissionsContext>
        </DataModelContext>,
    )
}

it("shows the export report button", async () => {
    history.push("?expanded=report_uuid:0")
    const { container } = renderReportTitle()
    expect(screen.getByText(/Export report/)).toBeInTheDocument()
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
        await userEvent.type(screen.getByLabelText(/Report title/), "New title{Enter}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 12,
        })
        expectFetch("post", "report/report_uuid/attribute/title", { title: "New title" })
    })

    it("sets the subtitle", async () => {
        renderReportTitle()
        await userEvent.type(screen.getByLabelText(/Report subtitle/), "New subtitle{Enter}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 12,
        })
        expectFetch("post", "report/report_uuid/attribute/subtitle", { subtitle: "New subtitle" })
    })

    it("sets the comment", async () => {
        renderReportTitle()
        await userEvent.type(screen.getByLabelText(/Comment/), "New comment{Shift>}{Enter}", {
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
        await userEvent.type(screen.getByLabelText("Unknown"), "4{Enter}}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 1,
        })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { unknown: 4 },
        })
    })

    it("sets the target not met status reaction time", async () => {
        renderReportTitle()
        await userEvent.type(screen.getByLabelText("Target not met"), "5{Enter}}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 1,
        })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { target_not_met: 5 },
        })
    })

    it("sets the near target met status reaction time", async () => {
        renderReportTitle()
        await userEvent.type(screen.getByLabelText("Near target met"), "6{Enter}}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 2,
        })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { near_target_met: 6 },
        })
    })

    it("sets the tech debt target status reaction time", async () => {
        renderReportTitle()
        await userEvent.type(screen.getByLabelText(/Technical debt target met/), "6{Enter}}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 2,
        })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { debt_target_met: 6 },
        })
    })

    it("sets the confirmed measurement entity status reaction time", async () => {
        renderReportTitle()
        await userEvent.type(screen.getByLabelText("Confirmed"), "60{Enter}}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 3,
        })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { confirmed: 60 },
        })
    })

    it("sets the false positive measurement entity status reaction time", async () => {
        renderReportTitle()
        await userEvent.type(screen.getByLabelText("False positive"), "70{Enter}}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 3,
        })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { false_positive: 70 },
        })
    })

    it("sets the fixed measurement entity status reaction time", async () => {
        renderReportTitle()
        await userEvent.type(screen.getByLabelText("Fixed"), "80{Enter}}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 3,
        })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { fixed: 80 },
        })
    })

    it("sets the won't fixed measurement entity status reaction time", async () => {
        renderReportTitle()
        await userEvent.type(screen.getByLabelText("Won't fix"), "90{Enter}}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 3,
        })
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
        fireEvent.mouseDown(screen.getByLabelText(/Issue tracker type/))
        const listbox = within(screen.getByRole("listbox"))
        await act(async () => fireEvent.click(listbox.getByText(/Jira/)))
        expectFetch("post", "report/report_uuid/issue_tracker/type", { type: "jira" })
    })

    it("sets the issue tracker url", async () => {
        renderReportTitle({ issueTrackerType: "jira" })
        await userEvent.type(screen.getByLabelText(/URL/), "https://jira{Enter}")
        expectFetch("post", "report/report_uuid/issue_tracker/url", { url: "https://jira" })
    })

    it("sets the issue tracker username", async () => {
        renderReportTitle({ issueTrackerType: "jira" })
        await userEvent.type(screen.getByLabelText(/Username/), "janedoe{Enter}")
        expectFetch("post", "report/report_uuid/issue_tracker/username", { username: "janedoe" })
    })

    it("sets the issue tracker password", async () => {
        renderReportTitle({ issueTrackerType: "jira" })
        await userEvent.type(screen.getByLabelText(/Password/), "secret{Enter}")
        expectFetch("post", "report/report_uuid/issue_tracker/password", { password: "secret" })
    })

    it("sets the issue tracker private token", async () => {
        renderReportTitle({ issueTrackerType: "jira" })
        await userEvent.type(screen.getByLabelText(/Private token/), "secret{Enter}")
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
