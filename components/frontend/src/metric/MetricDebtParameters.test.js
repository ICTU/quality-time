import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import * as fetch_server_api from "../api/fetch_server_api"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { MetricDebtParameters } from "./MetricDebtParameters"

jest.mock("../api/fetch_server_api.js")

const data_model = {
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
    },
}

function renderMetricDebtParameters({ accept_debt = false } = {}) {
    render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <DataModel.Provider value={data_model}>
                <MetricDebtParameters
                    metric={{
                        type: "violations",
                        tags: [],
                        accept_debt: accept_debt,
                        scale: "count",
                        issue_ids: [],
                        issue_status: [],
                    }}
                    metric_uuid="metric_uuid"
                    reload={jest.fn()}
                    report={{ subjects: {} }}
                />
            </DataModel.Provider>
        </Permissions.Provider>,
    )
}

it("accepts technical debt", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true })
    renderMetricDebtParameters()
    await userEvent.type(screen.getByLabelText(/Accept technical debt/), "Yes{Enter}")
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith(
        "post",
        "metric/metric_uuid/attribute/accept_debt",
        { accept_debt: true },
    )
})

it("accepts technical debt and sets target and end date", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true })
    renderMetricDebtParameters()
    await userEvent.type(screen.getByLabelText(/Accept technical debt/), "Yes, and{Enter}")
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/debt", {
        accept_debt: true,
    })
})

it("unaccepts technical debt and resets target and end date", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true })
    renderMetricDebtParameters({ accept_debt: true })
    await userEvent.type(screen.getByLabelText(/Accept technical debt/), "No, and{Enter}")
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/debt", {
        accept_debt: false,
    })
})

it("adds a comment", async () => {
    renderMetricDebtParameters()
    await userEvent.type(screen.getByLabelText(/Comment/), "Keep cool{Tab}")
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "metric/metric_uuid/attribute/comment", {
        comment: "Keep cool",
    })
})

it("sets the technical debt end date", async () => {
    // Suppress "Warning: An update to t inside a test was not wrapped in act(...)." caused by interacting with
    // the date picker.
    const consoleLog = console.log
    console.error = jest.fn()
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true })
    renderMetricDebtParameters()
    await userEvent.type(screen.getByPlaceholderText(/YYYY-MM-DD/), "2022-12-31{Tab}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 10,
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith(
        "post",
        "metric/metric_uuid/attribute/debt_end_date",
        { debt_end_date: "2022-12-31" },
    )
    console.log = consoleLog
})
