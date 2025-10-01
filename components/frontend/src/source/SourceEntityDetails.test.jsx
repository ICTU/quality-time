import { LocalizationProvider } from "@mui/x-date-pickers"
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs"
import { fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import dayjs from "dayjs"
import { vi } from "vitest"

import * as sourceApi from "../api/source"
import { EDIT_ENTITY_PERMISSION, Permissions } from "../context/Permissions"
import { clickText, expectNoAccessibilityViolations, expectText } from "../testUtils"
import { SourceEntityDetails } from "./SourceEntityDetails"

const reload = vi.fn

function renderSourceEntityDetails({ report = null, statusEndDate = null } = {}) {
    return render(
        <LocalizationProvider dateAdapter={AdapterDayjs}>
            <Permissions.Provider value={[EDIT_ENTITY_PERMISSION]}>
                <SourceEntityDetails
                    metricUuid="metric_uuid"
                    sourceUuid="source_uuid"
                    entity={{ key: "key" }}
                    status="unconfirmed"
                    name="violation"
                    reload={reload}
                    report={report}
                    statusEndDate={statusEndDate}
                />
            </Permissions.Provider>
        </LocalizationProvider>,
    )
}

beforeEach(() => {
    vi.spyOn(sourceApi, "setSourceEntityAttribute")
})

it("shows the default desired response times when the report has no desired response times", async () => {
    const { container } = renderSourceEntityDetails()
    fireEvent.mouseDown(screen.getByText("Unconfirm"))
    const expectedMenuItemDescriptions = [
        "This violation has been reviewed and should be addressed within 180 days.",
        "Ignore this violation for 7 days because it has been fixed or will be fixed shortly.",
        'Ignore this "violation" for 180 days because it has been incorrectly identified as violation.',
        "Ignore this violation for 180 days because it will not be fixed.",
    ]
    expectedMenuItemDescriptions.forEach((description) => {
        expectText(description)
    })
    await expectNoAccessibilityViolations(container)
})

it("shows the configured desired response times", async () => {
    const report = { desired_response_times: { confirmed: "2", fixed: "4", false_positive: "600", wont_fix: "100" } }
    const { container } = renderSourceEntityDetails({ report: report })
    fireEvent.mouseDown(screen.getByText("Unconfirm"))
    const expectedMenuItemDescriptions = [
        "This violation has been reviewed and should be addressed within 2 days.",
        "Ignore this violation for 4 days because it has been fixed or will be fixed shortly.",
        'Ignore this "violation" for 600 days because it has been incorrectly identified as violation.',
        "Ignore this violation for 100 days because it will not be fixed.",
    ]
    expectedMenuItemDescriptions.forEach((description) => {
        expectText(description)
    })
    await expectNoAccessibilityViolations(container)
})

it("shows no desired response times when the report has been configured to not have desired response times", async () => {
    const report = { desired_response_times: { confirmed: null, fixed: null, false_positive: null, wont_fix: null } }
    const { container } = renderSourceEntityDetails({ report: report })
    fireEvent.mouseDown(screen.getByText("Unconfirm"))
    const expectedMenuItemDescriptions = [
        "This violation has been reviewed and should be addressed.",
        "Ignore this violation because it has been fixed or will be fixed shortly.",
        'Ignore this "violation" because it has been incorrectly identified as violation.',
        "Ignore this violation because it will not be fixed.",
    ]
    expectedMenuItemDescriptions.forEach((description) => {
        expectText(description)
    })
    await expectNoAccessibilityViolations(container)
})

it("changes the entity status", async () => {
    const { container } = renderSourceEntityDetails()
    fireEvent.mouseDown(screen.getByText("Unconfirm"))
    clickText(/Confirm/)
    expect(sourceApi.setSourceEntityAttribute).toHaveBeenCalledWith(
        "metric_uuid",
        "source_uuid",
        "key",
        "status",
        "confirmed",
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("shows the entity status end date", async () => {
    const { container } = renderSourceEntityDetails({ statusEndDate: "20250112" })
    expect(screen.queryAllByDisplayValue("01/12/2025").length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("changes the entity status end date", async () => {
    const { container } = renderSourceEntityDetails()
    await userEvent.type(screen.getAllByLabelText(/Violation status end date/)[0], "01012222{Enter}")
    expect(sourceApi.setSourceEntityAttribute).toHaveBeenCalledWith(
        "metric_uuid",
        "source_uuid",
        "key",
        "status_end_date",
        dayjs("2222-01-01"),
        reload,
    )
    await expectNoAccessibilityViolations(container)
})

it("changes the rationale", async () => {
    const { container } = renderSourceEntityDetails()
    await userEvent.type(screen.getByLabelText(/rationale/), "Rationale")
    await userEvent.tab()
    expect(sourceApi.setSourceEntityAttribute).toHaveBeenCalledWith(
        "metric_uuid",
        "source_uuid",
        "key",
        "rationale",
        "Rationale",
        reload,
    )
    await expectNoAccessibilityViolations(container)
})
