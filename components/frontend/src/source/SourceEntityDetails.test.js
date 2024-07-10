import { fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import * as source from "../api/source"
import { EDIT_ENTITY_PERMISSION, Permissions } from "../context/Permissions"
import { SourceEntityDetails } from "./SourceEntityDetails"

jest.mock("../api/source.js")

const reload = jest.fn

function renderSourceEntityDetails(report) {
    render(
        <Permissions.Provider value={[EDIT_ENTITY_PERMISSION]}>
            <SourceEntityDetails
                metric_uuid="metric_uuid"
                source_uuid="source_uuid"
                entity={{ key: "key" }}
                status="unconfirmed"
                name="violation"
                reload={reload}
                report={report}
            />
        </Permissions.Provider>,
    )
}

it("shows the default desired response times when the report has no desired response times", () => {
    renderSourceEntityDetails()
    fireEvent.click(screen.getByText(/Unconfirmed/))
    const expectedMenuItemDescriptions = [
        "This violation has been reviewed and should be addressed within 180 days.",
        "Ignore this violation for 7 days because it has been fixed or will be fixed shortly.",
        'Ignore this "violation" for 180 days because it has been incorrectly identified as violation.',
        "Ignore this violation for 180 days because it will not be fixed.",
    ]
    expectedMenuItemDescriptions.forEach((description) => {
        expect(screen.queryAllByText(description).length).toBe(1)
    })
})

it("shows the configured desired response times", () => {
    const report = { desired_response_times: { confirmed: "2", fixed: "4", false_positive: "600", wont_fix: "100" } }
    renderSourceEntityDetails(report)
    fireEvent.click(screen.getByText(/Unconfirmed/))
    const expectedMenuItemDescriptions = [
        "This violation has been reviewed and should be addressed within 2 days.",
        "Ignore this violation for 4 days because it has been fixed or will be fixed shortly.",
        'Ignore this "violation" for 600 days because it has been incorrectly identified as violation.',
        "Ignore this violation for 100 days because it will not be fixed.",
    ]
    expectedMenuItemDescriptions.forEach((description) => {
        expect(screen.queryAllByText(description).length).toBe(1)
    })
})

it("shows no desired response times when the report has been configured to not have desired response times", () => {
    const report = { desired_response_times: { confirmed: null, fixed: null, false_positive: null, wont_fix: null } }
    renderSourceEntityDetails(report)
    fireEvent.click(screen.getByText(/Unconfirmed/))
    const expectedMenuItemDescriptions = [
        "This violation has been reviewed and should be addressed.",
        "Ignore this violation because it has been fixed or will be fixed shortly.",
        'Ignore this "violation" because it has been incorrectly identified as violation.',
        "Ignore this violation because it will not be fixed.",
    ]
    expectedMenuItemDescriptions.forEach((description) => {
        expect(screen.queryAllByText(description).length).toBe(1)
    })
})

it("changes the entity status", () => {
    source.set_source_entity_attribute = jest.fn()
    renderSourceEntityDetails()
    fireEvent.click(screen.getByText(/Confirm/))
    expect(source.set_source_entity_attribute).toHaveBeenCalledWith(
        "metric_uuid",
        "source_uuid",
        "key",
        "status",
        "confirmed",
        reload,
    )
})

it("changes the entity status end date", async () => {
    // Suppress "Warning: An update to t inside a test was not wrapped in act(...)." caused by interacting with
    // the date picker.
    const consoleLog = console.log
    console.error = jest.fn()
    source.set_source_entity_attribute = jest.fn()
    renderSourceEntityDetails()
    await userEvent.type(screen.getByPlaceholderText(/YYYY-MM-DD/), "2222-01-01{Tab}", {
        initialSelectionStart: 0,
        initialSelectionEnd: 10,
    })
    expect(source.set_source_entity_attribute).toHaveBeenCalledWith(
        "metric_uuid",
        "source_uuid",
        "key",
        "status_end_date",
        "2222-01-01",
        reload,
    )
    console.log = consoleLog
})

it("changes the rationale", async () => {
    source.set_source_entity_attribute = jest.fn()
    renderSourceEntityDetails()
    await userEvent.type(screen.getByPlaceholderText(/Rationale/), "Rationale")
    await userEvent.tab()
    expect(source.set_source_entity_attribute).toHaveBeenCalledWith(
        "metric_uuid",
        "source_uuid",
        "key",
        "rationale",
        "Rationale",
        reload,
    )
})
