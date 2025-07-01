import { LocalizationProvider } from "@mui/x-date-pickers"
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs"
import { fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as fetchServerApi from "../api/fetch_server_api"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectNoAccessibilityViolations } from "../testUtils"
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
    placeholder = "placeholder",
    warning = false,
}) {
    return render(
        <LocalizationProvider dateAdapter={AdapterDayjs}>
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <SourceParameter
                    parameter={parameter}
                    parameterKey={parameterKey}
                    parameterValue={parameterValue}
                    parameterValues={parameterValues}
                    placeholder={placeholder}
                    report={report}
                    requiredPermissions={[EDIT_REPORT_PERMISSION]}
                    source={{ type: "source_type" }}
                    sourceUuid="source_uuid"
                    warning={warning}
                />
            </Permissions.Provider>
        </LocalizationProvider>,
    )
}

beforeEach(() => vi.spyOn(fetchServerApi, "fetchServerApi").mockResolvedValue({ ok: true }))

it("renders an url parameter", async () => {
    const { container } = renderSourceParameter({})
    expect(screen.queryAllByLabelText(/URL/).length).toBe(1)
    expect(screen.getByDisplayValue(/https:\/\/test/)).toBeValid()
    await expectNoAccessibilityViolations(container)
})

it("renders an url parameter with warning", async () => {
    const { container } = renderSourceParameter({ warning: true })
    expect(screen.queryAllByLabelText(/URL/).length).toBe(1)
    expect(screen.getByDisplayValue(/https:\/\/test/)).not.toBeValid()
    await expectNoAccessibilityViolations(container)
})

it("renders a string parameter", async () => {
    const { container } = renderSourceParameter({ parameter: { name: "String", type: "string" } })
    expect(screen.queryAllByLabelText(/String/).length).toBe(1)
    expect(screen.queryAllByDisplayValue(/https/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders a password parameter", async () => {
    const { container } = renderSourceParameter({ parameter: { name: "Password", type: "password" } })
    expect(screen.queryAllByLabelText(/Password/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders a date parameter", async () => {
    const { container } = renderSourceParameter({
        parameter: { name: "Date", type: "date" },
        parameterValue: "2021-10-10",
    })
    expect(screen.queryAllByLabelText(/Date/, { selector: "input" }).length).toBe(1)
    expect(screen.queryAllByDisplayValue("10/10/2021").length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders a date parameter without date", async () => {
    const { container } = renderSourceParameter({ parameter: { name: "Date", type: "date" }, parameterValue: "" })
    expect(screen.queryAllByLabelText(/Date/, { selector: "input" }).length).toBe(1)
    expect(screen.queryAllByPlaceholderText(/YYYY/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("renders an integer parameter", async () => {
    const { container } = renderSourceParameter({ parameter: { name: "Integer", type: "integer" } })
    expect(screen.queryAllByLabelText(/Integer/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("doesn't change an integer parameter with mouse wheel", async () => {
    const { container } = renderSourceParameter({
        parameter: { name: "Integer", type: "integer" },
        parameterValue: "10",
    })
    fireEvent.wheel(screen.getByLabelText(/Integer/, { target: { scrollLeft: 500 } }))
    expect(fetchServerApi.fetchServerApi).not.toHaveBeenCalled()
    await expectNoAccessibilityViolations(container)
})

it("renders a single choice parameter", async () => {
    const { container } = renderSourceParameter({
        parameter: { name: "Single choice", type: "single_choice", values: ["option 1", "option 2"] },
        parameterValue: "option 1",
    })
    expect(screen.queryAllByLabelText(/Single choice/).length).toBe(1)
    expect(screen.queryAllByText(/option 1/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders a multiple choice parameter with default", async () => {
    const { container } = renderSourceParameter({
        parameter: {
            name: "Multiple choice",
            type: "multiple_choice_with_defaults",
            values: ["option 1", "option 2"],
            default_value: ["option 1"],
        },
        parameterValue: null,
    })
    expect(screen.queryAllByLabelText(/Multiple choice/).length).toBe(1)
    expect(screen.queryAllByText(/option 1/).length).toBe(1)
    expect(screen.queryAllByText(/option 2/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("renders a multiple choice parameter without defaults", async () => {
    const { container } = renderSourceParameter({
        parameter: {
            name: "Multiple choice",
            type: "multiple_choice_without_defaults",
            values: ["option 1", "option 2"],
        },
        parameterValue: [],
    })
    expect(screen.queryAllByLabelText(/Multiple choice/).length).toBe(1)
    expect(screen.queryAllByText(/option 1/).length).toBe(0)
    expect(screen.queryAllByText(/option 2/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("renders a multiple choice with addition parameter", async () => {
    const { container } = renderSourceParameter({
        parameter: { name: "Multiple choice with addition", type: "multiple_choice_with_addition" },
        parameterValue: ["option 1", "option 2"],
    })
    expect(screen.queryAllByLabelText(/Multiple choice/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders nothing on unknown parameter type", async () => {
    const { container } = renderSourceParameter({ parameter: { name: "Unknown", type: "unknown" } })
    expect(screen.queryAllByText(/Unknown/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("renders a help url", async () => {
    const { container } = renderSourceParameter({
        parameter: { name: "String", type: "string", help_url: "https://help" },
    })
    expect(screen.queryAllByTitle(/Opens new window/)[0].closest("a").href).toBe("https://help/")
    await expectNoAccessibilityViolations(container)
})

it("renders a help text", async () => {
    const { container } = renderSourceParameter({ parameter: { name: "String", type: "string", help: "Help text" } })
    expect(screen.queryAllByText(/Help text/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("changes the value", async () => {
    const { container } = renderSourceParameter({})
    await userEvent.type(screen.getByLabelText(/URL/), "/new{Enter}")
    expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith("post", "source/source_uuid/parameter/key1", {
        key1: "https://test/new",
        edit_scope: "source",
    })
    await expectNoAccessibilityViolations(container)
})

it("changes the value via mass edit", async () => {
    const { container } = renderSourceParameter({})
    fireEvent.click(screen.getByLabelText(/Edit scope/))
    fireEvent.click(screen.getByText(/Apply change to subject/))
    await userEvent.type(screen.getByLabelText(/URL/), "/new{Enter}")
    expect(fetchServerApi.fetchServerApi).toHaveBeenLastCalledWith("post", "source/source_uuid/parameter/key1", {
        key1: "https://test/new",
        edit_scope: "subject",
    })
    await expectNoAccessibilityViolations(container)
})

it("closes the mass edit menu", async () => {
    const { container } = renderSourceParameter({})
    fireEvent.click(screen.getByLabelText(/Edit scope/))
    await userEvent.keyboard("{Escape}")
    expect(fetchServerApi.fetchServerApi).not.toHaveBeenCalled()
    await expectNoAccessibilityViolations(container)
})
