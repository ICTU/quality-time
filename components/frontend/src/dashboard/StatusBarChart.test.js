import { fireEvent, queryAllByRole, queryAllByText, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { MetricSummaryCard } from "./MetricSummaryCard"

function renderBarChart(maxY, red) {
    const summary = {
        "2023-01-02": { blue: 0, red: red, green: 0, yellow: 0, white: 0, grey: 0 },
        "2023-01-01": { blue: 0, red: red, green: 0, yellow: 0, white: 0, grey: 0 },
    }
    return render(<MetricSummaryCard maxY={maxY} summary={summary} />)
}

const dateString = new Date("2023-01-02").toLocaleDateString()

it("shows the number of metrics per status when the total is zero", () => {
    renderBarChart(0, 0)
    expect(screen.queryAllByLabelText(`Status on ${dateString}: no metrics`, { exact: false }).length).toBe(1)
})

it("shows the number of metrics per status when the total is not zero", () => {
    renderBarChart(10, 0)
    expect(screen.queryAllByLabelText(`Status on ${dateString}: no metrics`, { exact: false }).length).toBe(1)
})

it("shows the number of metrics per status", () => {
    renderBarChart(2, 2)
    expect(
        screen.queryAllByLabelText(`Status on ${dateString}: 2 metrics, 2 target not met`, {
            exact: false,
        }).length,
    ).toBe(1)
})

it("shows the tooltip and hides it on click", async () => {
    const { container } = renderBarChart(2, 2)
    const targetNotMetBar = queryAllByRole(container, "presentation")[4]
    const targetNotMetLabel = "Target not met: 2 metrics"
    await userEvent.hover(targetNotMetBar)
    expect(queryAllByText(container, targetNotMetLabel).length).toBe(1)
    fireEvent.click(targetNotMetBar)
    expect(queryAllByText(container, targetNotMetLabel).length).toBe(0)
})
