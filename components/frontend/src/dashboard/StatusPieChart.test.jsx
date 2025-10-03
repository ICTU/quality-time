import { ThemeProvider } from "@mui/material/styles"
import { queryAllByRole, queryAllByText, render } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { expectLabelText, expectNoAccessibilityViolations } from "../testUtils"
import { theme } from "../theme"
import { MetricSummaryCard } from "./MetricSummaryCard"

function renderPieChart({ summary = { blue: 0, red: 0, green: 0, yellow: 0, white: 0, grey: 0 } } = {}) {
    return render(
        <ThemeProvider theme={theme}>
            <MetricSummaryCard summary={{ "2023-01-01": summary }} />
        </ThemeProvider>,
    )
}

const dateString = new Date("2023-01-01").toLocaleDateString()

it("shows there are no metrics", async () => {
    const { container } = renderPieChart()
    expectLabelText(`Status on ${dateString}: no metrics.`)
    await expectNoAccessibilityViolations(container)
})

it("shows the number of metrics per status", async () => {
    const { container } = renderPieChart({ summary: { blue: 2, red: 1, green: 2, yellow: 3, white: 1, grey: 1 } })
    expectLabelText(
        `Status on ${dateString}: 10 metrics, 2 target met, 1 target not met, 3 near target, 1 with accepted technical debt, 2 informative, 1 with unknown status.`,
    )
    await expectNoAccessibilityViolations(container)
})

it("shows the tooltip", async () => {
    const { container } = renderPieChart({ summary: { blue: 2, red: 1, green: 2, yellow: 3, white: 1, grey: 1 } })
    const unknownPie = queryAllByRole(container, "presentation")[0]
    const unknownLabel = "Unknown"
    await userEvent.hover(unknownPie)
    expect(queryAllByText(container, unknownLabel).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})
