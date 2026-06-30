import { LocalizationProvider } from "@mui/x-date-pickers"
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs"
import { render } from "@testing-library/react"
import dayjs from "dayjs"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { DataModelContext } from "../context/DataModel"
import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import {
    clickButton,
    clickLabeledElement,
    clickRole,
    enterLabeledText,
    expectFetch,
    expectNoAccessibilityViolations,
    expectNoFetch,
    expectText,
    mouseDownLabeledElement,
    typeLabeledText,
} from "../testUtils"
import { MetricDebtParameters } from "./MetricDebtParameters"

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
            name: "Source version",
            default_scale: "version_number",
            scales: ["version_number"],
        },
    },
}

function renderMetricDebtParameters({ acceptDebt = false, debtEndDate = null } = {}) {
    return render(
        <LocalizationProvider dateAdapter={AdapterDayjs}>
            <PermissionsContext value={[EDIT_REPORT_PERMISSION]}>
                <DataModelContext value={dataModel}>
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
                </DataModelContext>
            </PermissionsContext>
            ,
        </LocalizationProvider>,
    )
}

beforeEach(() => {
    vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true })
})

it("has no accessibility violations", async () => {
    const { container } = renderMetricDebtParameters()
    await expectNoAccessibilityViolations(container)
})

it("accepts technical debt", async () => {
    renderMetricDebtParameters()
    await enterLabeledText(/Accept technical debt/, "Yes")
    expectFetch("post", "metric/metric_uuid/attribute/accept_debt", { accept_debt: true })
})

it("accepts technical debt and sets target and end date", async () => {
    renderMetricDebtParameters()
    mouseDownLabeledElement(/Accept technical debt/)
    clickRole("option", /Yes, and/)
    expectFetch("post", "metric/metric_uuid/debt", { accept_debt: true })
})

it("unaccepts technical debt and resets target and end date", async () => {
    renderMetricDebtParameters({ acceptDebt: true })
    mouseDownLabeledElement(/Accept technical debt/)
    clickRole("option", /No, and/)
    expectFetch("post", "metric/metric_uuid/debt", { accept_debt: false })
})

it("adds a comment", async () => {
    renderMetricDebtParameters()
    await typeLabeledText(/Comment/, "Keep cool{Tab}")
    expectFetch("post", "metric/metric_uuid/attribute/comment", { comment: "Keep cool" })
})

it("undoes changes to a comment", async () => {
    renderMetricDebtParameters()
    await typeLabeledText(/Comment/, "Keep cool{Escape}")
    expectNoFetch()
})

it("sets the technical debt end date", async () => {
    renderMetricDebtParameters()
    await enterLabeledText(/Technical debt end date/, "12312022")
    expectFetch("post", "metric/metric_uuid/attribute/debt_end_date", { debt_end_date: dayjs("2022-12-31") })
})

it("sets the technical debt end date to today", async () => {
    renderMetricDebtParameters()
    clickLabeledElement(/Choose date/)
    clickButton("Today")
    expectFetch("post", "metric/metric_uuid/attribute/debt_end_date", {
        debt_end_date: dayjs().startOf("day"),
    })
})

it("shows days ago for the technical debt end date", async () => {
    renderMetricDebtParameters({ debtEndDate: "2000-01-01" })
    expectText(/years ago/)
})
