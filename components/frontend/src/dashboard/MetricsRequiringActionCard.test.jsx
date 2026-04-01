import { render, screen } from "@testing-library/react"

import { expectNoAccessibilityViolations, expectText } from "../testUtils"
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
    return render(<MetricsRequiringActionCard reports={[report]} selected={selected} />)
}

it("has no accessibility violations", async () => {
    const { container } = renderMetricsRequiringActionCard()
    await expectNoAccessibilityViolations(container)
})

it("shows the correct title", async () => {
    renderMetricsRequiringActionCard()
    expectText(/Action required/)
})

it("shows the title as selected when the card is selected", async () => {
    renderMetricsRequiringActionCard({ selected: true })
    expect(screen.getByText(/Action required/)).toHaveClass("selected")
})

it("shows the number of metrics", async () => {
    renderMetricsRequiringActionCard()
    expect(screen.getByRole("row", { name: "Unknown 0" })).toBeInTheDocument()
    expect(screen.getByRole("row", { name: "Target not met 1" })).toBeInTheDocument()
    expect(screen.getByRole("row", { name: "Near target met 2" })).toBeInTheDocument()
    expect(screen.getByRole("row", { name: "Total 3" })).toBeInTheDocument()
})
