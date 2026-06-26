import { render, screen } from "@testing-library/react"

import { expectNoAccessibilityViolations, expectRole, expectText } from "../testUtils"
import { IssuesCard } from "./IssuesCard"

const report = {
    subjects: {
        subject_uuid: {
            metrics: {
                metric_uuid: {
                    issue_ids: ["ID-1"],
                    issue_status: [{ issue_id: "ID-1", status_category: "doing" }],
                },
                another_metric_uuid: {
                    issue_ids: ["ID-1", "ID-2", "ID-3"],
                    issue_status: [
                        { issue_id: "ID-1", status_category: "doing" },
                        { issue_id: "ID-2", connection_error: "oops" },
                        { issue_id: "ID-4", status_category: "done" }, // Should be ignored
                    ],
                },
                metric_without_issues: { issue_ids: ["ID-5"] },
            },
        },
    },
}

function renderIssuesCard({ selected = false } = {}) {
    return render(<IssuesCard report={report} selected={selected} />)
}

it("has no accessibility violations", async () => {
    const { container } = renderIssuesCard()
    await expectNoAccessibilityViolations(container)
})

it("shows the correct title", async () => {
    renderIssuesCard()
    expectText(/Issues/)
})

it("shows the title as selected when the card is selected", async () => {
    renderIssuesCard({ selected: true })
    expect(screen.getByText(/Issues/)).toHaveClass("selected")
})

it("shows the number of issues", async () => {
    renderIssuesCard()
    expectRole("row", { name: "Todo 0" })
    expectRole("row", { name: "Doing 1" })
    expectRole("row", { name: "Done 0" })
    expectRole("row", { name: "Unknown 3" })
})
