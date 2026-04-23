import { LocalizationProvider } from "@mui/x-date-pickers"
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs"
import { fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import dayjs from "dayjs"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { EDIT_REPORT_PERMISSION, PermissionsContext } from "../context/Permissions"
import {
    clickButton,
    clickLabeledElement,
    clickText,
    expectFetch,
    expectNoAccessibilityViolations,
    expectNoFetch,
    expectNoText,
    expectText,
} from "../testUtils"
import { SourceParameter } from "./SourceParameter"

const report = {
    subjects: {
        subject_uuid: {
            metrics: {
                metric_uuid: {
                    sources: {
                        source_uuid: {
                            type: "source_type",
                            parameters: { key1: "" },
                        },
                        other_source_uuid: {
                            type: "source_type",
                            parameters: { key1: "value" },
                        },
                        another_source_uuid: {
                            type: "source_type",
                            parameters: { key1: ["value1", "value2"] },
                        },
                        yet_another_source_uuid: { type: "other_source_type" },
                    },
                },
            },
        },
    },
}

function renderSourceParameter({
    parameter = { name: "URL", type: "url" },
    parameterKey = "key1",
    parameterValue = "https://test",
    parameterValues = [],
    permissions = [EDIT_REPORT_PERMISSION],
    placeholder = "placeholder",
    recurrenceFrequency = null,
    recurrenceOffset = null,
    recurrenceUnit = null,
    warning = false,
}) {
    return render(
        <LocalizationProvider dateAdapter={AdapterDayjs}>
            <PermissionsContext value={permissions}>
                <SourceParameter
                    parameter={parameter}
                    parameterKey={parameterKey}
                    parameterValue={parameterValue}
                    parameterValues={parameterValues}
                    placeholder={placeholder}
                    report={report}
                    requiredPermissions={[EDIT_REPORT_PERMISSION]}
                    source={{
                        type: "source_type",
                        parameters: {
                            recurrence_frequency: recurrenceFrequency,
                            recurrence_offset: recurrenceOffset,
                            recurrence_unit: recurrenceUnit,
                        },
                    }}
                    sourceUuid="source_uuid"
                    warning={warning}
                />
            </PermissionsContext>
        </LocalizationProvider>,
    )
}

beforeEach(() => vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true }))

it("has no accessibility violations", async () => {
    const { container } = renderSourceParameter({})
    await expectNoAccessibilityViolations(container)
})

it("renders an URL parameter", async () => {
    renderSourceParameter({})
    expect(screen.queryAllByLabelText(/URL/).length).toBe(1)
    expect(screen.getByDisplayValue(/https:\/\/test/)).toBeValid()
})

it("renders an URL parameter with warning", async () => {
    renderSourceParameter({ warning: true })
    expect(screen.queryAllByLabelText(/URL/).length).toBe(1)
    expect(screen.getByDisplayValue(/https:\/\/test/)).not.toBeValid()
})

it("renders a string parameter", async () => {
    renderSourceParameter({ parameter: { name: "String", type: "string" } })
    expect(screen.queryAllByLabelText(/String/).length).toBe(1)
    expect(screen.queryAllByDisplayValue(/https/).length).toBe(1)
})

it("renders a password parameter", async () => {
    renderSourceParameter({ parameter: { name: "Password", type: "password" } })
    expect(screen.queryAllByLabelText(/Password/).length).toBe(1)
})

it("renders a date parameter", async () => {
    renderSourceParameter({
        parameter: { name: "Date", type: "date" },
        parameterValue: "2021-10-10",
    })
    expect(screen.queryAllByLabelText(/Date/, { selector: "input" }).length).toBe(1)
    expect(screen.queryAllByDisplayValue("10/10/2021").length).toBe(1)
})

it("renders a date parameter without date", async () => {
    renderSourceParameter({ parameter: { name: "Date", type: "date" }, parameterValue: "" })
    expect(screen.queryAllByLabelText(/Date/, { selector: "input" }).length).toBe(1)
    expect(screen.queryAllByPlaceholderText(/YYYY/).length).toBe(0)
})

it("sets the date to today", async () => {
    renderSourceParameter({ parameter: { name: "Date", type: "date" }, parameterValue: "2021-10-10" })
    clickLabeledElement(/Choose date/)
    clickButton("Today")
    expectFetch("post", "source/source_uuid/parameter/key1", {
        edit_scope: "source",
        key1: dayjs().startOf("day"),
    })
})

it("sets the next date one day from previous date", async () => {
    renderSourceParameter({
        parameter: { name: "Date", type: "date" },
        parameterValue: "2025-10-10",
        recurrenceOffset: "previous date",
    })
    clickButton("Set next date")
    expectFetch("post", "source/source_uuid/parameter/key1", {
        edit_scope: "source",
        key1: dayjs("2025-10-10").add(1, "day"),
    })
})

it("sets the next date two weeks from previous date", async () => {
    renderSourceParameter({
        parameter: { name: "Date", type: "date" },
        parameterValue: "2025-10-10",
        recurrenceFrequency: 2,
        recurrenceOffset: "previous date",
        recurrenceUnit: "week",
    })
    clickButton("Set next date")
    expectFetch("post", "source/source_uuid/parameter/key1", {
        edit_scope: "source",
        key1: dayjs("2025-10-10").add(2, "week"),
    })
})

it("sets the next date three months from current date", async () => {
    vi.useFakeTimers()
    renderSourceParameter({
        parameter: { name: "Date", type: "date" },
        parameterValue: "2025-10-10",
        recurrenceFrequency: 3,
        recurrenceOffset: "today",
        recurrenceUnit: "month",
    })
    clickButton("Set next date")
    expectFetch("post", "source/source_uuid/parameter/key1", {
        edit_scope: "source",
        key1: dayjs().add(3, "month"),
    })
})

it("sets the next date a year from current date", async () => {
    vi.useFakeTimers()
    renderSourceParameter({
        parameter: { name: "Date", type: "date" },
        parameterValue: "2025-10-10",
        recurrenceUnit: "year",
    })
    clickButton("Set next date")
    expectFetch("post", "source/source_uuid/parameter/key1", {
        edit_scope: "source",
        key1: dayjs().add(1, "year"),
    })
})

it("cannot set the next date if the recurrence frequency has not been set", async () => {
    renderSourceParameter({
        parameter: { name: "Date", type: "date" },
        parameterValue: "2025-10-10",
        recurrenceFrequency: 0,
    })
    clickButton("Set next date")
    expectNoFetch()
})

it("cannot set the next date if the user is not logged in", async () => {
    renderSourceParameter({
        parameter: { name: "Date", type: "date" },
        parameterValue: "2025-10-10",
        permissions: [],
        recurrenceFrequency: "year",
    })
    clickButton("Set next date")
    expectNoFetch()
})

it("renders an integer parameter", async () => {
    renderSourceParameter({
        parameter: { name: "Integer", type: "integer" },
        parameterValue: "0",
    })
    expect(screen.queryAllByLabelText(/Integer/).length).toBe(1)
    expect(screen.getByLabelText(/Integer/)).toBeValid()
})

it("does not accept floats as number", async () => {
    renderSourceParameter({
        parameter: { name: "Integer", type: "integer" },
        parameterValue: "0.1",
    })
    expect(screen.queryAllByLabelText(/Integer/).length).toBe(1)
    expect(screen.getByLabelText(/Integer/)).not.toBeValid()
})

it("does not accept negative integers as number", async () => {
    renderSourceParameter({
        parameter: { name: "Integer", type: "integer" },
        parameterValue: "-1",
    })
    expect(screen.queryAllByLabelText(/Integer/).length).toBe(1)
    expect(screen.getByLabelText(/Integer/)).not.toBeValid()
})

it("doesn't change an integer parameter with mouse wheel", async () => {
    renderSourceParameter({
        parameter: { name: "Integer", type: "integer" },
        parameterValue: "10",
    })
    fireEvent.wheel(screen.getByLabelText(/Integer/, { target: { scrollLeft: 500 } }))
    expectNoFetch()
})

it("renders a single choice parameter", async () => {
    renderSourceParameter({
        parameter: { name: "Single choice", type: "single_choice", values: ["option 1", "option 2"] },
        parameterValue: "option 1",
    })
    expect(screen.queryAllByLabelText(/Single choice/).length).toBe(1)
    expectText(/option 1/)
})

it("renders a multiple choice parameter with default", async () => {
    renderSourceParameter({
        parameter: {
            name: "Multiple choice",
            type: "multiple_choice_with_defaults",
            values: ["option 1", "option 2"],
            default_value: ["option 1"],
        },
        parameterValue: null,
    })
    expect(screen.queryAllByLabelText(/Multiple choice/).length).toBe(1)
    expectText(/option 1/)
    expectNoText(/option 2/)
})

it("renders a multiple choice parameter without defaults", async () => {
    renderSourceParameter({
        parameter: {
            name: "Multiple choice",
            type: "multiple_choice_without_defaults",
            values: ["option 1", "option 2"],
        },
        parameterValue: [],
    })
    expect(screen.queryAllByLabelText(/Multiple choice/).length).toBe(1)
    expectNoText(/option 1/)
    expectNoText(/option 2/)
})

it("renders a multiple choice with addition parameter", async () => {
    renderSourceParameter({
        parameter: { name: "Multiple choice with addition", type: "multiple_choice_with_addition" },
        parameterValue: ["option 1", "option 2"],
    })
    expect(screen.queryAllByLabelText(/Multiple choice/).length).toBe(1)
})

it("renders nothing on unknown parameter type", async () => {
    renderSourceParameter({ parameter: { name: "Unknown", type: "unknown" } })
    expectNoText(/Unknown/)
})

it("renders a help url", async () => {
    renderSourceParameter({
        parameter: { name: "String", type: "string", help_url: "https://help" },
    })
    expect(screen.queryAllByTitle(/Opens new window/)[0].closest("a").href).toBe("https://help/")
})

it("renders a help text", async () => {
    renderSourceParameter({ parameter: { name: "String", type: "string", help: "Help text" } })
    expectText(/Help text/)
    vi.useRealTimers() // Prevent test timeout
})

it("changes the value", async () => {
    renderSourceParameter({})
    await userEvent.type(screen.getByLabelText(/URL/), "/new{Enter}")
    expectFetch("post", "source/source_uuid/parameter/key1", { key1: "https://test/new", edit_scope: "source" })
})

it("changes the value via mass edit", async () => {
    renderSourceParameter({})
    clickLabeledElement(/Edit scope/)
    clickText(/Apply change to subject/)
    await userEvent.type(screen.getByLabelText(/URL/), "/new{Enter}")
    expectFetch("post", "source/source_uuid/parameter/key1", { key1: "https://test/new", edit_scope: "subject" })
})

it("closes the mass edit menu", async () => {
    renderSourceParameter({})
    clickLabeledElement(/Edit scope/)
    await userEvent.keyboard("{Escape}")
    expectNoFetch()
})
