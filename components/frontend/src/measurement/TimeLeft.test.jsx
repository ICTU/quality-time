import { render } from "@testing-library/react"

import { dataModelWithCountScale as dataModel } from "../__fixtures__/fixtures"
import { DataModelContext } from "../context/DataModel"
import { expectNoAccessibilityViolations, expectNoText, expectText } from "../testUtils"
import { TimeLeft } from "./TimeLeft"

function renderTimeLeft(metric) {
    return render(
        <DataModelContext value={dataModel}>
            <TimeLeft metric={metric} report={{}} />
        </DataModelContext>,
    )
}

it("has no accessibility violations", async () => {
    const { container } = renderTimeLeft({
        status: "debt_target_met",
        status_start: "2022-01-01",
        debt_end_date: "3000-01-01",
    })
    await expectNoAccessibilityViolations(container)
})

it("does not render the time left if the status does not demand action", async () => {
    renderTimeLeft({ status: "target_met" })
    expectNoText(/day/)
})

it("does not render the time left if there is no status start date", async () => {
    renderTimeLeft({ status: "target_not_met" })
    expectNoText(/day/)
})

it("does render the time left if technical debt is accepted with an end date", async () => {
    renderTimeLeft({
        status: "debt_target_met",
        status_start: "2022-01-01",
        debt_end_date: "3000-01-01",
    })
    expectText(/day/)
})

it("does not render the time left if technical debt is accepted without an end date", async () => {
    renderTimeLeft({ status: "debt_target_met", status_start: "2022-01-01" })
    expectNoText(/day/)
})

it("renders 0 days left if the deadline is in the past", async () => {
    renderTimeLeft({ status: "target_not_met", status_start: "2022-01-01" })
    expectText(/0 days/)
})

it("renders the time left if status demands action", async () => {
    const now = new Date()
    renderTimeLeft({ status: "target_not_met", status_start: now.toISOString() })
    expectText(/days/)
})
