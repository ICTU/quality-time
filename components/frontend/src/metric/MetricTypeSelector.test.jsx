import { fireEvent, render, screen } from "@testing-library/react"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import { asyncClickText, expectFetch, expectNoAccessibilityViolations, expectText } from "../testUtils"
import { MetricTypeSelector } from "./MetricTypeSelector"

const dataModel = {
    subjects: {
        subject_type: {
            metrics: ["violations", "source_version"],
        },
    },
    metrics: {
        violations: {
            direction: "<",
            name: "Violations",
            default_scale: "count",
            scales: ["count", "percentage"],
        },
        source_version: {
            direction: "<",
            documentation: "extra documentation",
            name: "Source version",
            default_scale: "version_number",
            scales: ["version_number"],
        },
        unsupported: {
            direction: "<",
            name: "Unsupported",
            default_scale: "count",
            scales: ["count"],
        },
        failed_jobs: {
            name: "Failed CI-jobs",
        },
    },
}

function renderMetricTypeSelector({ metricType = "violations", permissions = [EDIT_REPORT_PERMISSION] } = {}) {
    return render(
        <PermissionsContext value={permissions}>
            <DataModelContext value={dataModel}>
                <MetricTypeSelector
                    subject={{ type: "subject_type", metrics: {} }}
                    metric={{ type: metricType }}
                    metricUuid="metric_uuid"
                    reload={vi.fn()}
                    report={{ subjects: {} }}
                />
            </DataModelContext>
        </PermissionsContext>,
    )
}

it("has no accessibility violations", async () => {
    const { container } = renderMetricTypeSelector()
    await expectNoAccessibilityViolations(container)
})

it("sets the metric type", async () => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true })
    renderMetricTypeSelector()
    fireEvent.click(screen.getByDisplayValue("Violations"))
    await asyncClickText("Source version")
    expectFetch("post", "metric/metric_uuid/attribute/type", { type: "source_version" })
})

it("shows the metric type read the docs URL", async () => {
    renderMetricTypeSelector()
    expectText(/Read the Docs/)
})

it("shows the metric type has extra documentation", async () => {
    renderMetricTypeSelector({ metricType: "source_version" })
    expectText(/for additional information on how to configure this metric type/)
})

it("uses the name of the metric type for the documentation link", async () => {
    renderMetricTypeSelector({ metricType: "failed_jobs" })
    const readTheDocsLink = screen.getByRole("link", { name: "Read the Docs" })
    expect(readTheDocsLink).toHaveAttribute("href", expect.stringContaining("#failed-ci-jobs"))
})
