import { render } from "@testing-library/react"

import { DataModelContext } from "../context/DataModel"
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
        <DataModelContext value={dataModel}>
            <TargetVisualiser metric={metric} />
        </DataModelContext>,
    )
}

function expectVisible(...matchers) {
    matchers.forEach((matcher) => expectText(matcher))
}

function expectNotVisible(...matchers) {
    matchers.forEach((matcher) => expectNoText(matcher))
}

it("has no accessibility violations", async () => {
    const { container } = renderVisualiser({ type: "violations", target: "1", near_target: "15" })
    await expectNoAccessibilityViolations(container)
})

it("visualises a metric without tech debt", () => {
    renderVisualiser({ type: "violations", target: "1", near_target: "15" })
    expectVisible(
        /Target met/,
        /≦ 1 violation$/,
        /Near target met/,
        /1 - 15 violations/,
        /Target not met/,
        /> 15 violations/,
    )
    expectNotVisible(/Debt target met/)
})

it("visualises a metric with tech debt", () => {
    renderVisualiser({
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
})

it("visualises a metric with tech debt if debt target is missing", () => {
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

it("visualises a metric with tech debt if debt target is null", () => {
    renderVisualiser({ type: "violations", target: "10", near_target: "20", accept_debt: true, debt_target: null })
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

it("svisualises a  metric with tech debt and null near target", () => {
    renderVisualiser({
        type: "violations",
        target: "1",
        near_target: null,
        debt_target: "15",
        accept_debt: true,
    })
    expectVisible(
        /Target met/,
        /≦ 1 violation$/,
        /Debt target met/,
        /1 - 15 violations/,
        /Target not met/,
        /> 15 violations/,
    )
    expectNotVisible(/Near target met/)
})

it("visualises a more-is-better metric with tech debt and null near target", () => {
    renderVisualiser({
        type: "violations",
        target: "15",
        near_target: null,
        debt_target: "10",
        accept_debt: true,
        direction: ">",
    })
    expectVisible(
        /Target not met/,
        /< 0 violations/,
        /Debt target met/,
        /10 - 15 violations/,
        /Target met/,
        /≧ 15 violations/,
    )
    expectNotVisible(/Near target met/)
})

it("visualises a metric with tech debt with end date", () => {
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

it("visualises a metric with tech debt with end date in the past", () => {
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

it("visualises a metric with tech debt completely overlapping near target", () => {
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

it("visualises a metric without tech debt and target completely overlapping near target", () => {
    renderVisualiser({ type: "violations", target: "10", near_target: "10" })
    expectVisible(/Target met/, /≦ 10 violations/, /Target not met/, /> 10 violations/)
    expectNotVisible(/Debt target met/, /Near target met/)
})

it("visualises a more-is-better metric without tech debt and null near target", () => {
    renderVisualiser({ type: "violations", target: "15", near_target: null, direction: ">" })
    expectVisible(/Target not met/, /< 0 violations/, /Target met/, /≧ 15 violations/)
    expectNotVisible(/Debt target met/, /Near target met/)
})

it("visualises a metric without tech debt and null target", () => {
    renderVisualiser({ type: "violations", target: null, near_target: "20" })
    expectVisible(/Target met/, /≦ 0 violations/, /Target not met/, /> 20 violations/)
    expectNotVisible(/Debt target met/)
})

it("visualises a more-is-better metric without tech debt", () => {
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

it("visualises a more-is-better metric with tech debt", () => {
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

it("visualises a more-is-better metric with tech debt and missing debt target", () => {
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

it("visualises a more-is-better metric with tech debt and null debt target", () => {
    renderVisualiser({
        type: "violations",
        target: "15",
        near_target: "5",
        accept_debt: true,
        debt_target: null,
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

it("visualises a more-is-better metric with tech debt completely overlapping near target", () => {
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

it("visualises a more-is-better metric without tech debt and target completely overlapping near target", () => {
    renderVisualiser({ type: "violations", target: "15", near_target: "15", direction: ">" })
    expectVisible(/Target not met/, /< 15 violations/, /Target met/, /≧ 15 violations/)
    expectNotVisible(/Near target met/, /Debt target met/)
})

it("visualises a more-is-better metric without tech debt and zero target completely overlapping near target", () => {
    renderVisualiser({ type: "violations", target: "0", near_target: "0", direction: ">" })
    expectVisible(/Target met/, /≧ 0 violations/)
    expectNotVisible(/Debt target met/, /Near target met/, /Target not met/)
})

it("visualises an informative metric", () => {
    renderVisualiser({ type: "violations", evaluate_targets: false })
    expectVisible(/Informative/, /violations are not evaluated/)
    expectNotVisible(/Target met/, /Debt target met/, /Near target met/, /Target not met/)
})
