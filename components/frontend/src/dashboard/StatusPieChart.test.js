import { queryAllByRole, queryAllByText, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { MetricSummaryCard } from "./MetricSummaryCard"

function renderPieChart({ summary = { blue: 0, red: 0, green: 0, yellow: 0, white: 0, grey: 0 } } = {}) {
    return render(<MetricSummaryCard summary={{ "2023-01-01": summary }} />)
}

const dateString = new Date("2023-01-01").toLocaleDateString()

it("shows there are no metrics", () => {
    renderPieChart()
    expect(screen.getAllByLabelText(`Status on ${dateString}: no metrics.`, { exact: false }).length).toBe(1)
})

it("shows the number of metrics per status", () => {
    renderPieChart({ summary: { blue: 2, red: 1, green: 2, yellow: 3, white: 1, grey: 1 } })
    expect(
        screen.getAllByLabelText(
            `Status on ${dateString}: 10 metrics, 2 target met, 1 target not met, 3 near target, 1 with accepted technical debt, 2 informative, 1 with unknown status.`,
            { exact: false },
        ).length,
    ).toBe(1)
})

it("shows the tooltip", async () => {
    const { container } = renderPieChart({ summary: { blue: 2, red: 1, green: 2, yellow: 3, white: 1, grey: 1 } })
    const unknownPie = queryAllByRole(container, "presentation")[0]
    const unknownLabel = "Unknown"
    await userEvent.hover(unknownPie)
    expect(queryAllByText(container, unknownLabel).length).toBe(1)
})
