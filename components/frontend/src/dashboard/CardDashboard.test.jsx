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

function renderCardDashboard({
    cards = [],
    initialLayout = [],
    saveLayout = vi.fn,
    permissions = [EDIT_REPORT_PERMISSION],
} = {}) {
    return render(
        <ThemeProvider theme={theme}>
            <PermissionsContext value={permissions}>
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
    expect(container.children[0].children).toHaveLength(0)
})

it("adds the card to the dashboard", async () => {
    const { container } = renderCardDashboard({ cards: [metricSummaryCard()] })
    expect(container.children).toHaveLength(1)
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
    // If the initial entry were ignored, the card would be placed fresh at y=0. Cards are positioned with top/left
    // instead of CSS transforms so that they don't fly in from the top left.
    const gridItem = container.querySelector(".react-grid-item")
    expect(gridItem.style.top).toBe("418px")
    expect(saveLayout).not.toHaveBeenCalled()
})

it("allows for dragging cards with the edit report permission", async () => {
    const { container } = renderCardDashboard({ cards: [metricSummaryCard()] })
    expect(container.querySelector(".react-grid-item")).toHaveClass("react-draggable")
})

it("does not allow for dragging cards without the edit report permission", async () => {
    const { container } = renderCardDashboard({ cards: [metricSummaryCard()], permissions: [] })
    expect(container.querySelector(".react-grid-item")).not.toHaveClass("react-draggable")
})
