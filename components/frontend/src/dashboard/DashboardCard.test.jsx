import { ThemeProvider } from "@mui/material/styles"
import { act, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import { expectNoAccessibilityViolations, expectNoRole, expectText } from "../testUtils"
import { theme } from "../theme"
import { DashboardCard } from "./DashboardCard"

function renderDashboardCard(props = {}) {
    return render(
        <ThemeProvider theme={theme}>
            <DashboardCard title="Card title" {...props}>
                <div>Card contents</div>
            </DashboardCard>
        </ThemeProvider>,
    )
}

// jsdom does not do layout, so fake every element being wider than its container and trigger a re-measure.
function fakeTruncation() {
    vi.spyOn(HTMLElement.prototype, "scrollWidth", "get").mockReturnValue(200)
    vi.spyOn(HTMLElement.prototype, "clientWidth", "get").mockReturnValue(100)
    act(() => {
        globalThis.dispatchEvent(new Event("resize"))
    })
}

// The title has pointer-events: none (to suppress Safari's native tooltip), so hover the card header instead, which
// lets the event bubble to the MUI tooltip wrapper.
function hoverHeader(text) {
    return userEvent.hover(screen.getByText(text).closest(".MuiCardHeader-root"))
}

afterEach(() => {
    vi.restoreAllMocks()
})

it("shows the title", () => {
    renderDashboardCard()
    expectText("Card title")
})

it("does not show a tooltip when the title fits", async () => {
    renderDashboardCard({ title: "Short" })
    await hoverHeader("Short")
    expectNoRole("tooltip")
})

it("shows a tooltip with the full title when the title is truncated", async () => {
    const longTitle = "A very long subject title that does not fit on a single line in the card"
    renderDashboardCard({ title: longTitle })
    fakeTruncation()
    await hoverHeader(longTitle)
    expect(await screen.findByRole("tooltip")).toHaveTextContent(longTitle)
})

it("does not show a tooltip when the title is not a string", async () => {
    const elementTitle = "Element title"
    renderDashboardCard({ title: <span>{elementTitle}</span> })
    fakeTruncation()
    await hoverHeader(elementTitle)
    expectNoRole("tooltip")
})

it("has no accessibility violations", async () => {
    const { container } = renderDashboardCard()
    await expectNoAccessibilityViolations(container)
})
