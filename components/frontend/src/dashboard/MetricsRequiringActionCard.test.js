import { render, screen } from "@testing-library/react"

import { MetricsRequiringActionCard } from "./MetricsRequiringActionCard"

const report = {
    subjects: {
        subject_uuid: {
            metrics: {
                metric_uuid: {
                    status: "target_not_met",
                },
                another_metric_uuid: {
                    status: "near_target_met",
                },
            },
        },
        another_subject_uuid: {
            metrics: {
                yet_another_metric_uuid: {
                    status: "near_target_met",
                },
            },
        },
    },
}

function renderMetricsRequiringActionCard({ selected = false } = {}) {
    render(<MetricsRequiringActionCard reports={[report]} selected={selected} />)
}

it("shows the correct title", () => {
    renderMetricsRequiringActionCard()
    expect(screen.getByText(/Action required/)).toBeInTheDocument()
})

it("shows the title as selected when the card is selected", () => {
    renderMetricsRequiringActionCard({ selected: true })
    expect(screen.getByText(/Action required/)).toHaveClass("selected")
})

it("shows the number of metrics", () => {
    renderMetricsRequiringActionCard()
    expect(screen.getByRole("row", { name: "Unknown 0" })).toBeInTheDocument()
    expect(screen.getByRole("row", { name: "Target not met 1" })).toBeInTheDocument()
    expect(screen.getByRole("row", { name: "Near target met 2" })).toBeInTheDocument()
    expect(screen.getByRole("row", { name: "Total 3" })).toBeInTheDocument()
})
