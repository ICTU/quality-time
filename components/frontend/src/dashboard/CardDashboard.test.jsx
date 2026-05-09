import { ThemeProvider } from "@mui/material/styles"
import { render } from "@testing-library/react"
import { vi } from "vitest"

import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import { clickText, expectNoAccessibilityViolations } from "../testUtils"
import { theme } from "../theme"
import { CardDashboard } from "./CardDashboard"
import { MetricSummaryCard } from "./MetricSummaryCard"
import { mockGetAnimations } from "./MockAnimations"

beforeEach(() => mockGetAnimations())

afterEach(() => vi.restoreAllMocks())

function metricSummaryCard(key = "card") {
    return (
        <MetricSummaryCard
            header="Card"
            key={key}
            summary={{ date: { blue: 0, red: 1, green: 2, yellow: 1, white: 0, grey: 0 } }}
        />
    )
}

function renderCardDashboard({ cards = [], initialLayout = [], saveLayout = vi.fn } = {}) {
    return render(
        <ThemeProvider theme={theme}>
            <PermissionsContext value={[EDIT_REPORT_PERMISSION]}>
                <div id="dashboard">
                    <CardDashboard cards={cards} initialLayout={initialLayout} saveLayout={saveLayout} />
                </div>
            </PermissionsContext>
        </ThemeProvider>,
    )
}

it("has no accessibility violations", async () => {
    const { container } = renderCardDashboard()
    await expectNoAccessibilityViolations(container)
})

it("returns null without cards", async () => {
    const { container } = renderCardDashboard()
    expect(container.children[0].children.length).toBe(0)
})

it("adds the card to the dashboard", async () => {
    const { container } = renderCardDashboard({ cards: [metricSummaryCard()] })
    expect(container.children.length).toBe(1)
})

it("does not save the layout after click", async () => {
    const saveLayout = vi.fn()
    renderCardDashboard({ cards: [metricSummaryCard()], saveLayout: saveLayout })
    clickText("Card")
    expect(saveLayout).not.toHaveBeenCalled()
})

it("reuses initial layout entries for matching cards", async () => {
    const saveLayout = vi.fn()
    const { container } = renderCardDashboard({
        cards: [metricSummaryCard()],
        initialLayout: [{ i: "card", h: 6, w: 4, x: 8, y: 12 }],
        saveLayout: saveLayout,
    })
    // y=12 with rowHeight 24 + default margin 10 → pixel y = 12*24 + 12*10 + 10 = 418px.
    // If the initial entry were ignored, the card would be placed fresh at y=0.
    const gridItem = container.querySelector(".react-grid-item")
    expect(gridItem.style.transform).toContain("418px")
    expect(saveLayout).not.toHaveBeenCalled()
})
