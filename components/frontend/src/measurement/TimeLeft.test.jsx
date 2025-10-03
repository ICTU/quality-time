import { render } from "@testing-library/react"

import { expectNoAccessibilityViolations, expectNoText, expectText } from "../testUtils"
import { TimeLeft } from "./TimeLeft"

it("does not render the time left if the status does not demand action", async () => {
    const { container } = render(<TimeLeft metric={{ status: "target_met" }} report={{}} />)
    expectNoText(/day/)
    await expectNoAccessibilityViolations(container)
})

it("does not render the time left if there is no status start date", async () => {
    const { container } = render(<TimeLeft metric={{ status: "target_not_met" }} report={{}} />)
    expectNoText(/day/)
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
    expectText(/day/)
    await expectNoAccessibilityViolations(container)
})

it("does not render the time left if technical debt is accepted without an end date", async () => {
    const { container } = render(
        <TimeLeft metric={{ status: "debt_target_met", status_start: "2022-01-01" }} report={{}} />,
    )
    expectNoText(/day/)
    await expectNoAccessibilityViolations(container)
})

it("renders 0 days left if the deadline is in the past", async () => {
    const { container } = render(
        <TimeLeft metric={{ status: "target_not_met", status_start: "2022-01-01" }} report={{}} />,
    )
    expectText(/0 days/)
    await expectNoAccessibilityViolations(container)
})

it("renders the time left if status demands action", async () => {
    const now = new Date()
    const { container } = render(
        <TimeLeft metric={{ status: "target_not_met", status_start: now.toISOString() }} report={{}} />,
    )
    expectText(/days/)
    await expectNoAccessibilityViolations(container)
})
