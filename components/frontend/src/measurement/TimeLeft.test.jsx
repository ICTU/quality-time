import { render } from "@testing-library/react"

import { expectNoAccessibilityViolations, expectNoText, expectText } from "../testUtils"
import { TimeLeft } from "./TimeLeft"

it("has no accessibility violations", async () => {
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
    await expectNoAccessibilityViolations(container)
})

it("does not render the time left if the status does not demand action", async () => {
    render(<TimeLeft metric={{ status: "target_met" }} report={{}} />)
    expectNoText(/day/)
})

it("does not render the time left if there is no status start date", async () => {
    render(<TimeLeft metric={{ status: "target_not_met" }} report={{}} />)
    expectNoText(/day/)
})

it("does render the time left if technical debt is accepted with an end date", async () => {
    render(
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
})

it("does not render the time left if technical debt is accepted without an end date", async () => {
    render(<TimeLeft metric={{ status: "debt_target_met", status_start: "2022-01-01" }} report={{}} />)
    expectNoText(/day/)
})

it("renders 0 days left if the deadline is in the past", async () => {
    render(<TimeLeft metric={{ status: "target_not_met", status_start: "2022-01-01" }} report={{}} />)
    expectText(/0 days/)
})

it("renders the time left if status demands action", async () => {
    const now = new Date()
    render(<TimeLeft metric={{ status: "target_not_met", status_start: now.toISOString() }} report={{}} />)
    expectText(/days/)
})
