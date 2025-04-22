import { act, fireEvent, render, screen, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import history from "history/browser"
import { vi } from "vitest"

import { createTestableSettings } from "../__fixtures__/fixtures"
import * as fetchServerApi from "../api/fetch_server_api"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectFetch, expectNoAccessibilityViolations } from "../testUtils"
import { ReportTitle } from "./ReportTitle"

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true })
})

function renderReportTitle({ tags = ["foo"] } = {}) {
    return render(
        <DataModel.Provider value={{ sources: { jira: { name: "Jira", issue_tracker: true } } }}>
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <ReportTitle
                    report={{
                        report_uuid: "report_uuid",
                        title: "Report",
                        subjects: { subject_uuid: { metrics: { metric_uuid: { tags: tags } } } },
                    }}
                    reload={vi.fn()}
                    settings={createTestableSettings()}
                />
            </Permissions.Provider>
        </DataModel.Provider>,
    )
}

it("deletes the report", async () => {
    history.push("?expanded=report_uuid:0")
    const { container } = renderReportTitle()
    await act(async () => {
        fireEvent.click(screen.getByText(/Delete report/))
    })
    expectFetch("delete", "report/report_uuid", {})
    expect(history.location.search).toEqual("")
    await expectNoAccessibilityViolations(container)
})

describe("configuration tab", () => {
    beforeEach(() => history.push("?expanded=report_uuid:0"))

    it("sets the title", async () => {
        const { container } = renderReportTitle()
        await userEvent.type(screen.getByLabelText(/Report title/), "New title{Enter}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 12,
        })
        expectFetch("post", "report/report_uuid/attribute/title", { title: "New title" })
        await expectNoAccessibilityViolations(container)
    })

    it("sets the subtitle", async () => {
        const { container } = renderReportTitle()
        await userEvent.type(screen.getByLabelText(/Report subtitle/), "New subtitle{Enter}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 12,
        })
        expectFetch("post", "report/report_uuid/attribute/subtitle", { subtitle: "New subtitle" })
        await expectNoAccessibilityViolations(container)
    })

    it("sets the comment", async () => {
        const { container } = renderReportTitle()
        await userEvent.type(screen.getByLabelText(/Comment/), "New comment{Shift>}{Enter}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 8,
        })
        expectFetch("post", "report/report_uuid/attribute/comment", { comment: "New comment" })
        await expectNoAccessibilityViolations(container)
    })
})

describe("desired reaction times tab", () => {
    beforeEach(() => history.push("?expanded=report_uuid:1"))

    it("sets the unknown status reaction time", async () => {
        const { container } = renderReportTitle()
        await act(async () => {
            fireEvent.click(screen.getByLabelText("Unknown"))
        })
        await userEvent.type(screen.getByLabelText("Unknown"), "4{Enter}}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 1,
        })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { unknown: 4 },
        })
        await expectNoAccessibilityViolations(container)
    })

    it("sets the target not met status reaction time", async () => {
        const { container } = renderReportTitle()
        await userEvent.type(screen.getByLabelText("Target not met"), "5{Enter}}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 1,
        })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { target_not_met: 5 },
        })
        await expectNoAccessibilityViolations(container)
    })

    it("sets the near target met status reaction time", async () => {
        const { container } = renderReportTitle()
        await userEvent.type(screen.getByLabelText("Near target met"), "6{Enter}}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 2,
        })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { near_target_met: 6 },
        })
        await expectNoAccessibilityViolations(container)
    })

    it("sets the tech debt target status reaction time", async () => {
        const { container } = renderReportTitle()
        await userEvent.type(screen.getByLabelText(/Technical debt target met/), "6{Enter}}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 2,
        })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { debt_target_met: 6 },
        })
        await expectNoAccessibilityViolations(container)
    })

    it("sets the confirmed measurement entity status reaction time", async () => {
        const { container } = renderReportTitle()
        await userEvent.type(screen.getByLabelText("Confirmed"), "60{Enter}}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 3,
        })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { confirmed: 60 },
        })
        await expectNoAccessibilityViolations(container)
    })

    it("sets the false positive measurement entity status reaction time", async () => {
        const { container } = renderReportTitle()
        await userEvent.type(screen.getByLabelText("False positive"), "70{Enter}}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 3,
        })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { false_positive: 70 },
        })
        await expectNoAccessibilityViolations(container)
    })

    it("sets the fixed measurement entity status reaction time", async () => {
        const { container } = renderReportTitle()
        await userEvent.type(screen.getByLabelText("Fixed"), "80{Enter}}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 3,
        })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { fixed: 80 },
        })
        await expectNoAccessibilityViolations(container)
    })

    it("sets the won't fixed measurement entity status reaction time", async () => {
        const { container } = renderReportTitle()
        await userEvent.type(screen.getByLabelText("Won't fix"), "90{Enter}}", {
            initialSelectionStart: 0,
            initialSelectionEnd: 3,
        })
        expectFetch("post", "report/report_uuid/attribute/desired_response_times", {
            desired_response_times: { wont_fix: 90 },
        })
        await expectNoAccessibilityViolations(container)
    })
})

describe("notification destinations tab", () => {
    beforeEach(() => history.push("?expanded=report_uuid:2"))

    it("shows the notification destinations", async () => {
        const { container } = renderReportTitle()
        expect(screen.getAllByText(/No notification destinations/).length).toBe(2)
        await expectNoAccessibilityViolations(container)
    })
})

describe("issue tracker tab", () => {
    beforeEach(() => history.push("?expanded=report_uuid:3"))

    it("sets the issue tracker type", async () => {
        fetchServerApi.fetchServerApi.mockImplementation(() =>
            Promise.resolve({ projects: [], issue_types: [], fields: [], epic_links: [] }),
        )
        const { container } = renderReportTitle()
        fireEvent.mouseDown(screen.getByLabelText(/Issue tracker type/))
        const listbox = within(screen.getByRole("listbox"))
        await act(async () => fireEvent.click(listbox.getByText(/Jira/)))
        expectFetch("post", "report/report_uuid/issue_tracker/type", { type: "jira" })
        await expectNoAccessibilityViolations(container)
    })

    it("sets the issue tracker url", async () => {
        const { container } = renderReportTitle()
        await userEvent.type(screen.getByLabelText(/URL/), "https://jira{Enter}")
        expectFetch("post", "report/report_uuid/issue_tracker/url", { url: "https://jira" })
        await expectNoAccessibilityViolations(container)
    })

    it("sets the issue tracker username", async () => {
        const { container } = renderReportTitle()
        await userEvent.type(screen.getByLabelText(/Username/), "janedoe{Enter}")
        expectFetch("post", "report/report_uuid/issue_tracker/username", { username: "janedoe" })
        await expectNoAccessibilityViolations(container)
    })

    it("sets the issue tracker password", async () => {
        const { container } = renderReportTitle()
        await userEvent.type(screen.getByLabelText(/Password/), "secret{Enter}")
        expectFetch("post", "report/report_uuid/issue_tracker/password", { password: "secret" })
        await expectNoAccessibilityViolations(container)
    })

    it("sets the issue tracker private token", async () => {
        const { container } = renderReportTitle()
        await userEvent.type(screen.getByLabelText(/Private token/), "secret{Enter}")
        expectFetch("post", "report/report_uuid/issue_tracker/private_token", { private_token: "secret" })
        await expectNoAccessibilityViolations(container)
    })
})

describe("sources tab", () => {
    beforeEach(() => history.push("?expanded=report_uuid:4"))

    it("shows the sources, if available", async () => {
        const { container } = renderReportTitle()
        expect(screen.getAllByText(/No sources have been configured yet/).length).toBe(1)
        await expectNoAccessibilityViolations(container)
    })
})

describe("tags tab", () => {
    beforeEach(() => history.push("?expanded=report_uuid:5"))

    it("shows the tags", async () => {
        const { container } = renderReportTitle()
        expect(screen.getAllByText(/Tags/).length).toBe(1)
        await expectNoAccessibilityViolations(container)
    })
})

describe("changelog tab", () => {
    beforeEach(() => history.push("?expanded=report_uuid:6"))

    it("loads the changelog", async () => {
        fetchServerApi.fetchServerApi.mockImplementation(() => Promise.resolve({ changelog: [] }))
        const { container } = renderReportTitle()
        expectFetch("get", "changelog/report/report_uuid/5")
        await expectNoAccessibilityViolations(container)
    })
})
