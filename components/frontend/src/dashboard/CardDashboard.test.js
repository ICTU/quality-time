import { fireEvent, render, screen } from "@testing-library/react"

import { DarkMode } from "../context/DarkMode"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { CardDashboard } from "./CardDashboard"
import { MetricSummaryCard } from "./MetricSummaryCard"
import { mockGetAnimations } from "./MockAnimations"

beforeEach(() => mockGetAnimations())

afterEach(() => jest.restoreAllMocks())

function renderCardDashboard({ cards = [], initialLayout = [], saveLayout = jest.fn } = {}) {
    return render(
        <DarkMode.Provider value={false}>
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <div id="dashboard">
                    <CardDashboard cards={cards} initialLayout={initialLayout} saveLayout={saveLayout} />
                </div>
            </Permissions.Provider>
        </DarkMode.Provider>,
    )
}

it("returns null without cards", () => {
    const { container } = renderCardDashboard()
    expect(container.children[0].children.length).toBe(0)
})

it("adds the card to the dashboard", () => {
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
})

it("does not save the layout after click", async () => {
    const mockCallback = jest.fn()
    renderCardDashboard({
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
    fireEvent.click(screen.getByText("Card"))
    expect(mockCallback).not.toHaveBeenCalled()
})
