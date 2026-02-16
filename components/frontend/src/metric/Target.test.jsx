import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectFetch, expectNoAccessibilityViolations, expectText } from "../testUtils"
import { Target } from "./Target"

const dataModel = {
    metrics: {
        violations: {
            direction: "<",
            name: "Violations",
            default_scale: "count",
            scales: ["count", "percentage"],
        },
        violations_with_default_target: {
            target: "100",
            direction: "<",
            name: "Violations",
            default_scale: "count",
            scales: ["count", "percentage"],
        },
        source_version: {
            direction: "<",
            name: "Source version",
            default_scale: "version_number",
            scales: ["version_number"],
        },
    },
}

function renderMetricTarget(metric) {
    return render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={dataModel}>
                <Target metric={metric} metricUuid="metric_uuid" targetType="target" reload={vi.fn()} />
            </DataModel.Provider>
        </Permissions.Provider>,
    )
}

async function typeInField(label, text) {
    await userEvent.type(screen.getByDisplayValue(label), `${text}{Enter}`, {
        initialSelectionStart: 0,
        initialSelectionEnd: 2,
    })
}

beforeEach(() => vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true }))

function expectMetricAttributePost(attribute, payload) {
    const endPoint = `metric/metric_uuid/attribute/${attribute}`
    expectFetch("post", endPoint, { [attribute]: payload })
}

it("sets the metric integer target", async () => {
    const { container } = renderMetricTarget({ type: "violations", target: "10" })
    await typeInField("10", "42")
    expectMetricAttributePost("target", "42")
    await expectNoAccessibilityViolations(container)
})

it("is valid when the metric integer target is not set", async () => {
    const { container } = renderMetricTarget({ type: "violations", target: "" })
    expect(screen.getByLabelText(/Metric target/)).toBeValid()
    await expectNoAccessibilityViolations(container)
})

it("sets the metric version target", async () => {
    const { container } = renderMetricTarget({ type: "source_version", target: "10" })
    await typeInField("10", "4.2")
    expectMetricAttributePost("target", "4.2")
    await expectNoAccessibilityViolations(container)
})

it("displays the default target if changed", async () => {
    const { container } = renderMetricTarget({ type: "violations_with_default_target" })
    expectText(/Default/)
    await expectNoAccessibilityViolations(container)
})
