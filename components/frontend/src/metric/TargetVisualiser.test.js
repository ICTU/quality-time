import { render, screen } from "@testing-library/react"

import { DataModel } from "../context/DataModel"
import { TargetVisualiser } from "./TargetVisualiser"

const dataModel = {
    metrics: {
        violations: {
            unit: "violations",
            direction: "<",
            name: "Violations",
            default_scale: "count",
            scales: ["count", "percentage"],
        },
        violations_with_default_target: {
            target: "100",
            unit: "violations",
            direction: "<",
            name: "Violations",
            default_scale: "count",
            scales: ["count", "percentage"],
        },
        source_version: {
            unit: "",
            direction: "<",
            name: "Source version",
            default_scale: "version_number",
            scales: ["version_number"],
        },
    },
}

function renderVisualiser(metric) {
    render(
        <DataModel.Provider value={dataModel}>
            <TargetVisualiser metric={metric} />
        </DataModel.Provider>,
    )
}

function expectVisible(...matchers) {
    matchers.forEach((matcher) => expect(screen.queryAllByText(matcher).length).toBe(1))
}

function expectNotVisible(...matchers) {
    matchers.forEach((matcher) => expect(screen.queryAllByText(matcher).length).toBe(0))
}

it("shows help for evaluated metric without tech debt", async () => {
    renderVisualiser({ type: "violations", target: "10", near_target: "15" })
    expectVisible(
        /Target met/,
        /≦ 10 violations/,
        /Near target met/,
        /10 - 15 violations/,
        /Target not met/,
        /> 15 violations/,
    )
    expectNotVisible(/Debt target met/)
})

it("shows help for evaluated metric with tech debt", async () => {
    renderVisualiser({
        type: "violations",
        target: "10",
        debt_target: "15",
        near_target: "20",
        accept_debt: true,
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
})

it("shows help for evaluated metric with tech debt if debt target is missing", async () => {
    renderVisualiser({ type: "violations", target: "10", near_target: "20", accept_debt: true })
    expectVisible(
        /Target met/,
        /≦ 10 violations/,
        /Near target met/,
        /10 - 20 violations/,
        /Target not met/,
        /> 20 violations/,
    )
    expectNotVisible(/Debt target met/)
})

it("shows help for evaluated metric with tech debt with end date", async () => {
    renderVisualiser({
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
})

it("shows help for evaluated metric with tech debt with end date in the past", async () => {
    renderVisualiser({
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
})

it("shows help for evaluated metric with tech debt completely overlapping near target", async () => {
    renderVisualiser({
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
})

it("shows help for evaluated metric without tech debt and target completely overlapping near target", async () => {
    renderVisualiser({ type: "violations", target: "10", near_target: "10" })
    expectVisible(/Target met/, /≦ 10 violations/, /Target not met/, /> 10 violations/)
    expectNotVisible(/Debt target met/, /Near target met/)
})

it("shows help for evaluated more-is-better metric without tech debt", async () => {
    renderVisualiser({ type: "violations", target: "15", near_target: "10", direction: ">" })
    expectVisible(
        /Target not met/,
        /< 10 violations/,
        /Near target met/,
        /10 - 15 violations/,
        /Target met/,
        /≧ 15 violations/,
    )
    expectNotVisible(/Debt target met/)
})

it("shows help for evaluated more-is-better metric with tech debt", async () => {
    renderVisualiser({
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
})

it("shows help for evaluated more-is-better metric with tech debt and missing debt target", async () => {
    renderVisualiser({
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
})

it("shows help for evaluated more-is-better metric with tech debt completely overlapping near target", async () => {
    renderVisualiser({
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
})

it("shows help for evaluated more-is-better metric without tech debt and target completely overlapping near target", async () => {
    renderVisualiser({ type: "violations", target: "15", near_target: "15", direction: ">" })
    expectVisible(/Target not met/, /< 15 violations/, /Target met/, /≧ 15 violations/)
    expectNotVisible(/Near target met/, /Debt target met/)
})

it("shows help for evaluated metric without tech debt and zero target completely overlapping near target", async () => {
    renderVisualiser({ type: "violations", target: "0", near_target: "0", direction: ">" })
    expectVisible(/Target met/, /≧ 0 violations/)
    expectNotVisible(/Debt target met/, /Near target met/, /Target not met/)
})

it("shows help for informative metric", async () => {
    renderVisualiser({ type: "violations", evaluate_targets: false })
    expectVisible(/Informative/, /violations are not evaluated/)
    expectNotVisible(/Target met/, /Debt target met/, /Near target met/, /Target not met/)
})
