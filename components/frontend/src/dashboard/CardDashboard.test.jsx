import { ThemeProvider } from "@mui/material/styles"
import { render } from "@testing-library/react"
import { vi } from "vitest"

import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { clickText, expectNoAccessibilityViolations } from "../testUtils"
import { theme } from "../theme"
import { CardDashboard } from "./CardDashboard"
import { MetricSummaryCard } from "./MetricSummaryCard"
import { mockGetAnimations } from "./MockAnimations"

beforeEach(() => mockGetAnimations())

afterEach(() => vi.restoreAllMocks())

function renderCardDashboard({ cards = [], initialLayout = [], saveLayout = vi.fn } = {}) {
    return render(
        <ThemeProvider theme={theme}>
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <div id="dashboard">
                    <CardDashboard cards={cards} initialLayout={initialLayout} saveLayout={saveLayout} />
                </div>
            </Permissions.Provider>
        </ThemeProvider>,
    )
}

it("returns null without cards", async () => {
    const { container } = renderCardDashboard()
    expect(container.children[0].children.length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("adds the card to the dashboard", async () => {
    const { container } = renderCardDashboard({
        cards: [
            <MetricSummaryCard
                header="Card"
                key="card"
                summary={{
                    date: { blue: 0, red: 1, green: 2, yellow: 1, white: 0, grey: 0 },
                }}
            />,
        ],
    })
    expect(container.children.length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("does not save the layout after click", async () => {
    const mockCallback = vi.fn()
    const { container } = renderCardDashboard({
        cards: [
            <MetricSummaryCard
                header="Card"
                key="card"
                summary={{
                    date: { blue: 0, red: 1, green: 2, yellow: 1, white: 0, grey: 0 },
                }}
            />,
        ],
        initialLayout: [{ h: 6, w: 4, x: 0, y: 0 }],
        saveLayout: mockCallback,
    })
    clickText("Card")
    expect(mockCallback).not.toHaveBeenCalled()
    await expectNoAccessibilityViolations(container)
})
