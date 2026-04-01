import { act, fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import { clickText, expectFetch, expectNoAccessibilityViolations, expectNoText } from "../testUtils"
import { MetricConfigurationParameters } from "./MetricConfigurationParameters"

const dataModel = {
    scales: {
        count: { name: "Count" },
        percentage: { name: "Percentage" },
        version_number: { name: "Version number" },
    },
    subjects: {
        subject_type: {
            metrics: ["violations", "source_version"],
        },
    },
    metrics: {
        violations: {
            unit: "violations",
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

beforeEach(() => vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true }))

afterEach(() => vi.clearAllMocks())

async function renderMetricParameters(scale = "count") {
    let result
    await act(async () => {
        result = render(
            <PermissionsContext value={[EDIT_REPORT_PERMISSION]}>
                <DataModelContext value={dataModel}>
                    <MetricConfigurationParameters
                        subject={{ type: "subject_type" }}
                        metric={{
                            type: "violations",
                            scale: scale,
                        }}
                        metricUuid="metric_uuid"
                        reload={vi.fn()}
                        report={{ subjects: {} }}
                    />
                </DataModelContext>
            </PermissionsContext>,
        )
    })
    return result
}

async function typeInField(label, text, confirm = "Enter") {
    await userEvent.type(screen.getByLabelText(label), `${text}{${confirm}}`, {
        initialSelectionStart: 0,
        initialSelectionEnd: 11,
    })
}

function expectMetricAttributePost(attribute, payload) {
    const endPoint = `metric/metric_uuid/attribute/${attribute}`
    expectFetch("post", endPoint, { [attribute]: payload })
}

it("has no accessibility violations", async () => {
    const { container } = await renderMetricParameters()
    await expectNoAccessibilityViolations(container)
})

it("sets the metric name", async () => {
    await renderMetricParameters()
    await typeInField(/Metric name/, "New metric name")
    expectMetricAttributePost("name", "New metric name")
})

it("sets the metric secondary name", async () => {
    await renderMetricParameters()
    await typeInField(/Metric secondary name/, "New metric secondary name")
    expectMetricAttributePost("secondary_name", "New metric secondary name")
})

it("adds a tag on enter", async () => {
    await renderMetricParameters()
    await typeInField(/Metric tags/, "New tag", "Enter")
    expectMetricAttributePost("tags", ["New tag"])
})

it("adds a tag on tab", async () => {
    await renderMetricParameters()
    await typeInField(/Metric tags/, "New tag", "Tab")
    expectMetricAttributePost("tags", ["New tag"])
})

it("changes the scale", async () => {
    await renderMetricParameters()
    fireEvent.mouseDown(screen.getByLabelText(/Metric scale/))
    clickText(/Percentage/)
    expectMetricAttributePost("scale", "percentage")
})

it("changes the direction", async () => {
    await renderMetricParameters()
    fireEvent.mouseDown(screen.getByLabelText(/direction/))
    clickText(/More violations is better/)
    expectMetricAttributePost("direction", ">")
})

it("sets the metric unit for metrics with the count scale", async () => {
    await renderMetricParameters()
    await typeInField(/Metric unit plural/, "New metric units")
    expectMetricAttributePost("unit", "New metric units")
    await typeInField(/Metric unit singular/, "New metric unit")
    expectMetricAttributePost("unit_singular", "New metric unit")
})

it("sets the metric unit for metrics with the percentage scale", async () => {
    await renderMetricParameters("percentage")
    await typeInField(/Metric unit plural/, "New metric units")
    expectMetricAttributePost("unit", "New metric units")
    await typeInField(/Metric unit singular/, "New metric unit")
    expectMetricAttributePost("unit_singular", "New metric unit")
})

it("skips the metric unit fields for metrics with the version number scale", async () => {
    render(
        <DataModelContext value={dataModel}>
            <MetricConfigurationParameters
                report={{ subjects: {} }}
                subject={{ type: "subject_type" }}
                metric={{ type: "source_version" }}
                metricUuid="metric_uuid"
            />
        </DataModelContext>,
    )
    expectNoText(/Metric unit/)
})

it("turns off evaluation of targets", async () => {
    await renderMetricParameters()
    await userEvent.type(screen.getByLabelText(/Evaluate metric targets/), "No{Enter}")
    expectMetricAttributePost("evaluate_targets", false)
})
