import { render } from "@testing-library/react"

import { DataModel } from "../context/DataModel"
import {
    expectNoAccessibilityViolations,
    expectNoText,
    expectNoTextAfterWait,
    expectText,
    expectTextAfterWait,
    hoverText,
} from "../testUtils"
import { MeasurementTarget } from "./MeasurementTarget"

const dataModel = {
    metrics: {
        violations: { direction: "<", unit: "violations", unit_singular: "violation" },
        duration: { direction: "<", unit: "minutes", unit_singular: "minute" },
    },
}

function renderMeasurementTarget(metric) {
    return render(
        <DataModel.Provider value={dataModel}>
            <MeasurementTarget metric={metric} />
        </DataModel.Provider>,
    )
}

it("renders the target", async () => {
    const { container } = renderMeasurementTarget({ type: "violations" })
    expectText(/≦ 0/)
    await expectNoAccessibilityViolations(container)
})

it("does not render the target if the metric is informative", async () => {
    const { container } = renderMeasurementTarget({ type: "violations", evaluate_targets: false })
    expectNoText(/≦ 0/)
    await expectNoAccessibilityViolations(container)
})

it("renders the target with minutes", async () => {
    const { container } = renderMeasurementTarget({ type: "duration" })
    expectText(/≦ 0/)
    await expectNoAccessibilityViolations(container)
})

it("renders the target with minutes percentage", async () => {
    const { container } = renderMeasurementTarget({ type: "duration", scale: "percentage" })
    expectText(/≦ 0%/)
    await expectNoAccessibilityViolations(container)
})

it("does not render the technical debt popup if technical debt is not accepted", async () => {
    const { container } = renderMeasurementTarget({ type: "violations", target: "100", debt_end_date: "2022-12-31" })
    await hoverText(/100/)
    await expectNoTextAfterWait(/accepted as technical debt/)
    await expectNoAccessibilityViolations(container)
})

it("renders the technical debt popup if technical debt is accepted", async () => {
    const { container } = renderMeasurementTarget({
        type: "violations",
        debt_target: "50",
        target: "100",
        accept_debt: true,
        debt_end_date: "2021-12-31",
    })
    await hoverText(/100/)
    await expectTextAfterWait(/Measurements ≦ 50 violations are accepted as technical debt/)
    await expectNoAccessibilityViolations(container)
})

it("uses the singular unit in the technical debt popup if the technical debt target is one", async () => {
    const { container } = renderMeasurementTarget({
        type: "violations",
        debt_target: "1",
        target: "100",
        accept_debt: true,
        debt_end_date: "2021-12-31",
    })
    await hoverText(/100/)
    await expectTextAfterWait(/Measurements ≦ 1 violation are accepted as technical debt/)
    await expectNoAccessibilityViolations(container)
})

it("renders the technical debt popup if technical debt is accepted with a future end date", async () => {
    const { container } = renderMeasurementTarget({
        type: "violations",
        target: "100",
        accept_debt: true,
        debt_end_date: "3000-01-01",
    })
    await hoverText(/100/)
    await expectTextAfterWait(/accepted as technical debt until/)
    await expectNoAccessibilityViolations(container)
})

it("renders the issue status if all issues are done", async () => {
    const { container } = renderMeasurementTarget({
        type: "violations",
        target: "100",
        accept_debt: true,
        issue_status: [{ status_category: "done" }],
    })
    await hoverText(/100/)
    await expectTextAfterWait(/all issues for this metric have been marked done/)
    await expectNoAccessibilityViolations(container)
})

it("does not render the issue status if technical debt is not accepted", async () => {
    const { container } = renderMeasurementTarget({
        type: "violations",
        target: "100",
        issue_status: [{ status_category: "done" }],
    })
    await hoverText(/100/)
    await expectNoTextAfterWait(/all issues for this metric have been marked done/)
    await expectNoAccessibilityViolations(container)
})

it("renders both the issue status and the technical debt end date", async () => {
    const { container } = renderMeasurementTarget({
        type: "violations",
        target: "100",
        accept_debt: true,
        debt_end_date: "2021-12-31",
        issue_status: [{ status_category: "done" }],
    })
    await hoverText(/100/)
    await expectTextAfterWait(/all issues for this metric have been marked done and technical debt was accepted/)
    await expectNoAccessibilityViolations(container)
})

it("does not crash when the technical end date is invalid", async () => {
    const { container } = renderMeasurementTarget({
        type: "violations",
        target: "100",
        accept_debt: true,
        debt_end_date: "2021-13-",
    })
    await hoverText(/100/)
    await expectTextAfterWait(/Measurements ≦ 0 violations are accepted as technical debt/)
    await expectNoAccessibilityViolations(container)
})
