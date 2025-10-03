import { render, screen } from "@testing-library/react"

import { expectNoAccessibilityViolations, expectText } from "../testUtils"
import { IssuesCard } from "./IssuesCard"

const report = {
    subjects: {
        subject_uuid: {
            metrics: {
                metric_uuid: {
                    issue_ids: ["ID-1"],
                    issue_status: [{ status_category: "doing" }],
                },
                another_metric_uuid: {
                    issue_ids: ["ID-2", "ID-3"],
                    issue_status: [{ connection_error: "oops" }],
                },
            },
        },
    },
}

function renderIssuesCard({ selected = false } = {}) {
    return render(<IssuesCard report={report} selected={selected} />)
}

it("shows the correct title", async () => {
    const { container } = renderIssuesCard()
    expectText(/Issues/)
    await expectNoAccessibilityViolations(container)
})

it("shows the title as selected when the card is selected", async () => {
    const { container } = renderIssuesCard({ selected: true })
    expect(screen.getByText(/Issues/)).toHaveClass("selected")
    await expectNoAccessibilityViolations(container)
})

it("shows the number of issues", async () => {
    const { container } = renderIssuesCard()
    expect(screen.getByRole("row", { name: "Todo 0" })).toBeInTheDocument()
    expect(screen.getByRole("row", { name: "Doing 1" })).toBeInTheDocument()
    expect(screen.getByRole("row", { name: "Done 0" })).toBeInTheDocument()
    expect(screen.getByRole("row", { name: "Unknown 2" })).toBeInTheDocument()
    await expectNoAccessibilityViolations(container)
})
