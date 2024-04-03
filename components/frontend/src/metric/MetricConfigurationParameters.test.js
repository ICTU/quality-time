import { act, fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { MetricConfigurationParameters } from "./MetricConfigurationParameters"
import * as fetch_server_api from "../api/fetch_server_api"

jest.mock("../api/fetch_server_api.js")

const data_model = {
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
            unit: "",
            direction: "<",
            name: "Source version",
            default_scale: "version_number",
            scales: ["version_number"],
        },
    },
}

function renderMetricParameters(
    scale = "count",
    issue_ids = [],
    report = { subjects: {} },
    permissions = [EDIT_REPORT_PERMISSION],
) {
    render(
        <Permissions.Provider value={permissions}>
            <DataModel.Provider value={data_model}>
                <MetricConfigurationParameters
                    subject={{ type: "subject_type" }}
                    metric={{
                        type: "violations",
                        tags: [],
                        accept_debt: false,
                        scale: scale,
                        issue_ids: issue_ids,
                    }}
                    metric_uuid="metric_uuid"
                    reload={() => {
                        /* Dummy implementation */
                    }}
                    report={report}
                />
            </DataModel.Provider>
        </Permissions.Provider>,
    )
}

it("sets the metric name", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true })
    await act(async () => {
        renderMetricParameters()
    })
    await userEvent.type(screen.getByLabelText(/Metric name/), "New metric name{Enter}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 11,
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith(
        "post",
        "metric/metric_uuid/attribute/name",
        { name: "New metric name" },
    )
})

it("adds a tag", async () => {
    await act(async () => {
        renderMetricParameters()
    })
    await userEvent.type(screen.getByLabelText(/Tags/), "New tag{Enter}")
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith(
        "post",
        "metric/metric_uuid/attribute/tags",
        { tags: ["New tag"] },
    )
})

it("changes the scale", async () => {
    await act(async () => {
        renderMetricParameters()
    })
    fireEvent.click(screen.getByText(/Metric scale/))
    fireEvent.click(screen.getByText(/Percentage/))
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith(
        "post",
        "metric/metric_uuid/attribute/scale",
        { scale: "percentage" },
    )
})

it("changes the direction", async () => {
    await act(async () => {
        renderMetricParameters()
    })
    fireEvent.click(screen.getByText(/direction/))
    fireEvent.click(screen.getByText(/More violations is better/))
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith(
        "post",
        "metric/metric_uuid/attribute/direction",
        { direction: ">" },
    )
})

it("sets the metric unit for metrics with the count scale", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true })
    await act(async () => {
        renderMetricParameters()
    })
    await userEvent.type(screen.getByLabelText(/Metric unit/), "New metric unit{Enter}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 11,
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith(
        "post",
        "metric/metric_uuid/attribute/unit",
        { unit: "New metric unit" },
    )
})

it("sets the metric unit field for metrics with the percentage scale", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true })
    await act(async () => {
        renderMetricParameters("percentage")
    })
    await userEvent.type(screen.getByLabelText(/Metric unit/), "New metric unit{Enter}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 11,
    })
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith(
        "post",
        "metric/metric_uuid/attribute/unit",
        { unit: "New metric unit" },
    )
})

it("skips the metric unit field for metrics with the version number scale", () => {
    render(
        <DataModel.Provider value={data_model}>
            <MetricConfigurationParameters
                report={{ subjects: {} }}
                subject={{ type: "subject_type" }}
                metric={{ type: "source_version", tags: [], accept_debt: false }}
                metric_uuid="metric_uuid"
            />
        </DataModel.Provider>,
    )
    expect(screen.queryAllByText(/Metric unit/).length).toBe(0)
})

it("turns off evaluation of targets", async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true })
    await act(async () => {
        renderMetricParameters()
    })
    await userEvent.type(screen.getByLabelText(/Evaluate metric targets/), "No{Enter}")
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith(
        "post",
        "metric/metric_uuid/attribute/evaluate_targets",
        { evaluate_targets: false },
    )
})
