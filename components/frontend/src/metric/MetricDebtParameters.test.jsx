import { LocalizationProvider } from "@mui/x-date-pickers"
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs"
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import dayjs from "dayjs"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { DataModel } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectNoAccessibilityViolations } from "../testUtils"
import { MetricDebtParameters } from "./MetricDebtParameters"

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
    },
}

function renderMetricDebtParameters({ acceptDebt = false, debtEndDate = null } = {}) {
    return render(
        <LocalizationProvider dateAdapter={AdapterDayjs}>
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <DataModel.Provider value={dataModel}>
                    <MetricDebtParameters
                        metric={{
                            accept_debt: acceptDebt,
                            debt_end_date: debtEndDate,
                            issue_ids: [],
                            issue_status: [],
                            scale: "count",
                            tags: [],
                            type: "violations",
                        }}
                        metricUuid="metric_uuid"
                        reload={vi.fn()}
                        report={{ subjects: {} }}
                    />
                </DataModel.Provider>
            </Permissions.Provider>
            ,
        </LocalizationProvider>,
    )
}

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true })
})

it("accepts technical debt", async () => {
    const { container } = renderMetricDebtParameters()
    await userEvent.type(screen.getByLabelText(/Accept technical debt/), "Yes{Enter}")
    expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith("post", "metric/metric_uuid/attribute/accept_debt", {
        accept_debt: true,
    })
    await expectNoAccessibilityViolations(container)
})

it("accepts technical debt and sets target and end date", async () => {
    const { container } = renderMetricDebtParameters()
    await userEvent.type(screen.getByLabelText(/Accept technical debt/), "Yes, and{Enter}")
    expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith("post", "metric/metric_uuid/debt", {
        accept_debt: true,
    })
    await expectNoAccessibilityViolations(container)
})

it("unaccepts technical debt and resets target and end date", async () => {
    const { container } = renderMetricDebtParameters({ acceptDebt: true })
    await userEvent.type(screen.getByLabelText(/Accept technical debt/), "No, and{Enter}")
    expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith("post", "metric/metric_uuid/debt", {
        accept_debt: false,
    })
    await expectNoAccessibilityViolations(container)
})

it("adds a comment", async () => {
    const { container } = renderMetricDebtParameters()
    await userEvent.type(screen.getByLabelText(/Comment/), "Keep cool{Tab}")
    expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith("post", "metric/metric_uuid/attribute/comment", {
        comment: "Keep cool",
    })
    await expectNoAccessibilityViolations(container)
})

it("undoes changes to a comment", async () => {
    const { container } = renderMetricDebtParameters()
    await userEvent.type(screen.getByLabelText(/Comment/), "Keep cool{Escape}")
    expect(fetchServerApi.fetchServerApi).not.toHaveBeenCalled()
    await expectNoAccessibilityViolations(container)
})

it("sets the technical debt end date", async () => {
    const { container } = renderMetricDebtParameters()
    await userEvent.type(screen.getByPlaceholderText(/YYYY/), "12312022{Enter}")
    expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith(
        "post",
        "metric/metric_uuid/attribute/debt_end_date",
        { debt_end_date: dayjs("2022-12-31") },
    )
    await expectNoAccessibilityViolations(container)
})

it("shows days ago for the technical debt end date", async () => {
    const { container } = renderMetricDebtParameters({ debtEndDate: "2000-01-01" })
    expect(screen.getAllByText(/years ago/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})
