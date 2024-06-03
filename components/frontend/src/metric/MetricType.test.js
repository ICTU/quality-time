import { act, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import * as fetch_server_api from "../api/fetch_server_api"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { MetricType } from "./MetricType"

jest.mock("../api/fetch_server_api.js")

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
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={dataModel}>
                <MetricType
                    subjectType="subject_type"
                    metricType={metricType}
                    metric_uuid="metric_uuid"
                    reload={() => {
                        /* Dummy implementation */
                    }}
                />
            </DataModel.Provider>
        </Permissions.Provider>,
    )
}

it("sets the metric type", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true })
    await act(async () => {
        renderMetricType("violations")
    })
    await userEvent.type(screen.getByRole("combobox"), "Source version{Enter}")
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/attribute/type", {
        type: "source_version",
    })
})

it("shows the metric type even when not supported by the subject type", async () => {
    await act(async () => {
        renderMetricType("unsupported")
    })
    expect(screen.queryAllByText(/Unsupported/).length).toBe(2)
})
