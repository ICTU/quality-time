import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectNoAccessibilityViolations } from "../testUtils"
import { MetricType } from "./MetricType"

const dataModel = {
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
            unit: "",
            direction: "<",
            documentation: "extra documentation",
            name: "Source version",
            default_scale: "version_number",
            scales: ["version_number"],
        },
        unsupported: {
            unit: "foo",
            direction: "<",
            name: "Unsupported",
            default_scale: "count",
            scales: ["count"],
        },
    },
}

function renderMetricType(metricType) {
    return render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={dataModel}>
                <MetricType
                    subjectType="subject_type"
                    metricType={metricType}
                    metricUuid="metric_uuid"
                    reload={vi.fn()}
                />
            </DataModel.Provider>
        </Permissions.Provider>,
    )
}

it("sets the metric type", async () => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true })
    const { container } = renderMetricType("violations")
    await userEvent.type(screen.getByRole("combobox"), "Source version{Enter}")
    expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith("post", "metric/metric_uuid/attribute/type", {
        type: "source_version",
    })
    await expectNoAccessibilityViolations(container)
})

it("shows the metric type even when not supported by the subject type", async () => {
    const { container } = renderMetricType("unsupported")
    expect(screen.queryAllByText(/Unsupported/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows the metric type read the docs URL", async () => {
    const { container } = renderMetricType("violations")
    expect(screen.queryAllByText(/Read the Docs/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("shows the metric type has extra documentation", async () => {
    const { container } = renderMetricType("source_version")
    expect(screen.queryAllByText(/for additional information on how to configure this metric type/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})
