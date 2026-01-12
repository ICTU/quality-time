import { render } from "@testing-library/react"

import { DataModel } from "../context/DataModel"
import { expectNoAccessibilityViolations, expectNoText, expectText } from "../testUtils"
import { TargetVisualiser } from "./TargetVisualiser"

const dataModel = {
    metrics: {
        violations: {
            unit: "violations",
            unit_singular: "violation",
            direction: "<",
            name: "Violations",
            default_scale: "count",
            scales: ["count", "percentage"],
        },
        violations_with_default_target: {
            target: "100",
            unit: "violations",
            unit_singular: "violation",
            direction: "<",
            name: "Violations",
            default_scale: "count",
            scales: ["count", "percentage"],
        },
        source_version: {
            unit: "",
            unit_singular: "",
            direction: "<",
            name: "Source version",
            default_scale: "version_number",
            scales: ["version_number"],
        },
    },
}

function renderVisualiser(metric) {
    return render(
        <DataModel.Provider value={dataModel}>
            <TargetVisualiser metric={metric} />
        </DataModel.Provider>,
    )
}

function expectVisible(...matchers) {
    matchers.forEach((matcher) => expectText(matcher))
}

function expectNotVisible(...matchers) {
    matchers.forEach((matcher) => expectNoText(matcher))
}

it("shows help for evaluated metric without tech debt", async () => {
    const { container } = renderVisualiser({ type: "violations", target: "1", near_target: "15" })
    expectVisible(
        /Target met/,
        /≦ 1 violation$/,
        /Near target met/,
        /1 - 15 violations/,
        /Target not met/,
        /> 15 violations/,
    )
    expectNotVisible(/Debt target met/)
    await expectNoAccessibilityViolations(container)
})

it("shows help for evaluated metric with tech debt", async () => {
    const { container } = renderVisualiser({
        type: "violations",
        target: "1",
        debt_target: "15",
        near_target: "20",
        accept_debt: true,
    })
    expectVisible(
        /Target met/,
        /≦ 1 violation$/,
        /Debt target met/,
        /1 - 15 violations/,
        /Near target met/,
        /15 - 20 violations/,
        /Target not met/,
        /> 20 violations/,
    )
    await expectNoAccessibilityViolations(container)
})

it("shows help for evaluated metric with tech debt if debt target is missing", async () => {
    const { container } = renderVisualiser({ type: "violations", target: "10", near_target: "20", accept_debt: true })
    expectVisible(
        /Target met/,
        /≦ 10 violations/,
        /Near target met/,
        /10 - 20 violations/,
        /Target not met/,
        /> 20 violations/,
    )
    expectNotVisible(/Debt target met/)
    await expectNoAccessibilityViolations(container)
})

it("shows help for evaluated metric with tech debt with end date", async () => {
    const { container } = renderVisualiser({
        type: "violations",
        target: "10",
        debt_target: "15",
        near_target: "20",
        accept_debt: true,
        debt_end_date: "3000-01-01",
    })
    expectVisible(
        /Target met/,
        /≦ 10 violations/,
        /Debt target met/,
        /10 - 15 violations/,
        /Near target met/,
        /15 - 20 violations/,
        /Target not met/,
        /> 20 violations/,
    )
    await expectNoAccessibilityViolations(container)
})

it("shows help for evaluated metric with tech debt with end date in the past", async () => {
    const { container } = renderVisualiser({
        type: "violations",
        target: "10",
        debt_target: "15",
        near_target: "20",
        accept_debt: true,
        debt_end_date: "2000-01-01",
    })
    expectVisible(
        /Target met/,
        /≦ 10 violations/,
        /Near target met/,
        /10 - 20 violations/,
        /Target not met/,
        /> 20 violations/,
    )
    expectNotVisible(/Debt target met/)
    await expectNoAccessibilityViolations(container)
})

it("shows help for evaluated metric with tech debt completely overlapping near target", async () => {
    const { container } = renderVisualiser({
        type: "violations",
        target: "10",
        debt_target: "20",
        near_target: "20",
        accept_debt: true,
    })
    expectVisible(
        /Target met/,
        /≦ 10 violations/,
        /Debt target met/,
        /10 - 20 violations/,
        /Target not met/,
        /> 20 violations/,
    )
    expectNotVisible(/Near target met/)
    await expectNoAccessibilityViolations(container)
})

it("shows help for evaluated metric without tech debt and target completely overlapping near target", async () => {
    const { container } = renderVisualiser({ type: "violations", target: "10", near_target: "10" })
    expectVisible(/Target met/, /≦ 10 violations/, /Target not met/, /> 10 violations/)
    expectNotVisible(/Debt target met/, /Near target met/)
    await expectNoAccessibilityViolations(container)
})

it("shows help for evaluated more-is-better metric without tech debt", async () => {
    const { container } = renderVisualiser({ type: "violations", target: "15", near_target: "10", direction: ">" })
    expectVisible(
        /Target not met/,
        /< 10 violations/,
        /Near target met/,
        /10 - 15 violations/,
        /Target met/,
        /≧ 15 violations/,
    )
    expectNotVisible(/Debt target met/)
    await expectNoAccessibilityViolations(container)
})

it("shows help for evaluated more-is-better metric with tech debt", async () => {
    const { container } = renderVisualiser({
        type: "violations",
        target: "15",
        near_target: "5",
        debt_target: "10",
        accept_debt: true,
        direction: ">",
    })
    expectVisible(
        /Target not met/,
        /< 5 violations/,
        /Near target met/,
        /5 - 10 violations/,
        /Debt target met/,
        /10 - 15 violations/,
        /Target met/,
        /≧ 15 violations/,
    )
    await expectNoAccessibilityViolations(container)
})

it("shows help for evaluated more-is-better metric with tech debt and missing debt target", async () => {
    const { container } = renderVisualiser({
        type: "violations",
        target: "15",
        near_target: "5",
        accept_debt: true,
        direction: ">",
    })
    expectVisible(
        /Target not met/,
        /< 5 violations/,
        /Near target met/,
        /5 - 15 violations/,
        /Target met/,
        /≧ 15 violations/,
    )
    expectNotVisible(/Debt target met/)
    await expectNoAccessibilityViolations(container)
})

it("shows help for evaluated more-is-better metric with tech debt completely overlapping near target", async () => {
    const { container } = renderVisualiser({
        type: "violations",
        target: "15",
        near_target: "5",
        debt_target: "5",
        accept_debt: true,
        direction: ">",
    })
    expectVisible(
        /Target not met/,
        /< 5 violations/,
        /Debt target met/,
        /5 - 15 violations/,
        /Target met/,
        /≧ 15 violations/,
    )
    expectNotVisible(/Near target met/)
    await expectNoAccessibilityViolations(container)
})

it("shows help for evaluated more-is-better metric without tech debt and target completely overlapping near target", async () => {
    const { container } = renderVisualiser({ type: "violations", target: "15", near_target: "15", direction: ">" })
    expectVisible(/Target not met/, /< 15 violations/, /Target met/, /≧ 15 violations/)
    expectNotVisible(/Near target met/, /Debt target met/)
    await expectNoAccessibilityViolations(container)
})

it("shows help for evaluated metric without tech debt and zero target completely overlapping near target", async () => {
    const { container } = renderVisualiser({ type: "violations", target: "0", near_target: "0", direction: ">" })
    expectVisible(/Target met/, /≧ 0 violations/)
    expectNotVisible(/Debt target met/, /Near target met/, /Target not met/)
    await expectNoAccessibilityViolations(container)
})

it("shows help for informative metric", async () => {
    const { container } = renderVisualiser({ type: "violations", evaluate_targets: false })
    expectVisible(/Informative/, /violations are not evaluated/)
    expectNotVisible(/Target met/, /Debt target met/, /Near target met/, /Target not met/)
    await expectNoAccessibilityViolations(container)
})
