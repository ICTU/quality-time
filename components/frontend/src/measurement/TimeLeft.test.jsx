import { render, screen } from "@testing-library/react"

import { expectNoAccessibilityViolations } from "../testUtils"
import { TimeLeft } from "./TimeLeft"

it("does not render the time left if the status does not demand action", async () => {
    const { container } = render(<TimeLeft metric={{ status: "target_met" }} report={{}} />)
    expect(screen.queryAllByText(/day/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("does not render the time left if there is no status start date", async () => {
    const { container } = render(<TimeLeft metric={{ status: "target_not_met" }} report={{}} />)
    expect(screen.queryAllByText(/day/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("does render the time left if technical debt is accepted with an end date", async () => {
    const { container } = render(
        <TimeLeft
            metric={{
                status: "debt_target_met",
                status_start: "2022-01-01",
                debt_end_date: "3000-01-01",
            }}
            report={{}}
        />,
    )
    expect(screen.queryAllByText(/day/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("does not render the time left if technical debt is accepted without an end date", async () => {
    const { container } = render(
        <TimeLeft metric={{ status: "debt_target_met", status_start: "2022-01-01" }} report={{}} />,
    )
    expect(screen.queryAllByText(/day/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("renders 0 days left if the deadline is in the past", async () => {
    const { container } = render(
        <TimeLeft metric={{ status: "target_not_met", status_start: "2022-01-01" }} report={{}} />,
    )
    expect(screen.queryAllByText(/0 days/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders the time left if status demands action", async () => {
    const now = new Date()
    const { container } = render(
        <TimeLeft metric={{ status: "target_not_met", status_start: now.toISOString() }} report={{}} />,
    )
    expect(screen.queryAllByText(/days/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})
