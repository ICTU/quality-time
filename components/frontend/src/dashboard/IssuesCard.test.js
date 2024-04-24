import { render, screen } from "@testing-library/react"

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
    render(<IssuesCard report={report} selected={selected} />)
}

it("shows the correct title", () => {
    renderIssuesCard()
    expect(screen.getByText(/Issues/)).toBeInTheDocument()
})

it("shows the title in blue when selected", () => {
    renderIssuesCard({ selected: true })
    expect(screen.getByText(/Issues/)).toHaveClass("blue")
})

it("shows the number of issues", () => {
    renderIssuesCard()
    expect(screen.getByRole("row", { name: "Todo 0" })).toBeInTheDocument()
    expect(screen.getByRole("row", { name: "Doing 1" })).toBeInTheDocument()
    expect(screen.getByRole("row", { name: "Done 0" })).toBeInTheDocument()
    expect(screen.getByRole("row", { name: "Unknown 2" })).toBeInTheDocument()
})
