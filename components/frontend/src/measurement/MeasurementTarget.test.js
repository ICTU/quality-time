import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { DataModel } from "../context/DataModel"
import { expectNoAccessibilityViolations } from "../testUtils"
import { MeasurementTarget } from "./MeasurementTarget"

const dataModel = {
    metrics: { violations: { direction: "<", unit: "violations" }, duration: { direction: "<", unit: "minutes" } },
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
    expect(screen.getAllByText(/≦ 0/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("does not render the target if the metric is informative", async () => {
    const { container } = renderMeasurementTarget({ type: "violations", evaluate_targets: false })
    expect(screen.queryAllByText(/≦ 0/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("renders the target with minutes", async () => {
    const { container } = renderMeasurementTarget({ type: "duration" })
    expect(screen.getAllByText(/≦ 0/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders the target with minutes percentage", async () => {
    const { container } = renderMeasurementTarget({ type: "duration", scale: "percentage" })
    expect(screen.getAllByText(/≦ 0%/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("does not render the technical debt popup if technical debt is not accepted", async () => {
    const { container } = renderMeasurementTarget({ type: "violations", target: "100", debt_end_date: "2022-12-31" })
    await userEvent.hover(screen.queryByText(/100/))
    await waitFor(() => {
        expect(screen.queryAllByText(/accepted as technical debt/).length).toBe(0)
    })
    await expectNoAccessibilityViolations(container)
})

it("renders the technical debt popup if technical debt is accepted", async () => {
    const { container } = renderMeasurementTarget({
        type: "violations",
        target: "100",
        accept_debt: true,
        debt_end_date: "2021-12-31",
    })
    await userEvent.hover(screen.queryByText(/100/))
    await waitFor(() => {
        expect(screen.queryAllByText(/accepted as technical debt/).length).toBe(1)
    })
    await expectNoAccessibilityViolations(container)
})

it("renders the technical debt popup if technical debt is accepted with a future end date", async () => {
    const { container } = renderMeasurementTarget({
        type: "violations",
        target: "100",
        accept_debt: true,
        debt_end_date: "3000-01-01",
    })
    await userEvent.hover(screen.queryByText(/100/))
    await waitFor(() => {
        expect(screen.queryAllByText(/accepted as technical debt until/).length).toBe(1)
    })
    await expectNoAccessibilityViolations(container)
})

it("renders the issue status if all issues are done", async () => {
    const { container } = renderMeasurementTarget({
        type: "violations",
        target: "100",
        accept_debt: true,
        issue_status: [{ status_category: "done" }],
    })
    await userEvent.hover(screen.queryByText(/100/))
    await waitFor(() => {
        expect(screen.queryAllByText(/all issues for this metric have been marked done/).length).toBe(1)
    })
    await expectNoAccessibilityViolations(container)
})

it("does not render the issue status if technical debt is not accepted", async () => {
    const { container } = renderMeasurementTarget({
        type: "violations",
        target: "100",
        issue_status: [{ status_category: "done" }],
    })
    await userEvent.hover(screen.queryByText(/100/))
    await waitFor(() => {
        expect(screen.queryAllByText(/all issues for this metric have been marked done/).length).toBe(0)
    })
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
    await userEvent.hover(screen.queryByText(/100/))
    await waitFor(() => {
        expect(
            screen.queryAllByText(/all issues for this metric have been marked done and technical debt was accepted/)
                .length,
        ).toBe(1)
    })
    await expectNoAccessibilityViolations(container)
})

it("does not crash when the technical end date is invalid", async () => {
    const { container } = renderMeasurementTarget({
        type: "violations",
        target: "100",
        accept_debt: true,
        debt_end_date: "2021-13-",
    })
    await userEvent.hover(screen.queryByText(/100/))
    await waitFor(() => {
        expect(screen.queryAllByText(/Measurements ≦ 0 violations are accepted as technical debt/).length).toBe(1)
    })
    await expectNoAccessibilityViolations(container)
})
