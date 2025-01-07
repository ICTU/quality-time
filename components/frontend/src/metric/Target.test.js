import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import * as fetch_server_api from "../api/fetch_server_api"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { Target } from "./Target"

jest.mock("../api/fetch_server_api.js")

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

function renderMetricTarget(metric) {
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={dataModel}>
                <Target
                    metric={metric}
                    metric_uuid="metric_uuid"
                    target_type="target"
                    reload={() => {
                        /* Dummy implementation */
                    }}
                />
            </DataModel.Provider>
        </Permissions.Provider>,
    )
}

it("sets the metric integer target", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true })
    renderMetricTarget({ type: "violations", target: "10" })
    await userEvent.type(screen.getByDisplayValue("10"), "42{Enter}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 2,
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/attribute/target", {
        target: "42",
    })
})

it("sets the metric version target", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true })
    renderMetricTarget({ type: "source_version", target: "10" })
    await userEvent.type(screen.getByDisplayValue("10"), "4.2{Enter}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 2,
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/attribute/target", {
        target: "4.2",
    })
})

it("displays the default target if changed", () => {
    renderMetricTarget({ type: "violations_with_default_target" })
    expect(screen.queryAllByText(/Default/).length).toBe(1)
})
