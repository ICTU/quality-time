import { LocalizationProvider } from "@mui/x-date-pickers"
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs"
import { fireEvent, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { vi } from "vitest"

import * as fetch_server_api from "../api/fetch_server_api"
import { EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { expectNoAccessibilityViolations } from "../testUtils"
import { SourceParameter } from "./SourceParameter"

vi.mock("../api/fetch_server_api.js")

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
    help = "",
    help_url = "",
    parameter_key = "key1",
    parameter_name = "URL",
    parameter_type = "url",
    parameter_value = "https://test",
    parameter_values = [],
    placeholder = "placeholder",
    warning = false,
}) {
    return render(
        <LocalizationProvider dateAdapter={AdapterDayjs}>
            <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
                <SourceParameter
                    help={help}
                    help_url={help_url}
                    parameter_key={parameter_key}
                    parameter_name={parameter_name}
                    parameter_type={parameter_type}
                    parameter_value={parameter_value}
                    parameter_values={parameter_values}
                    placeholder={placeholder}
                    report={report}
                    requiredPermissions={[EDIT_REPORT_PERMISSION]}
                    source={{ type: "source_type" }}
                    source_uuid="source_uuid"
                    warning={warning}
                />
            </Permissions.Provider>
        </LocalizationProvider>,
    )
}

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
    const { container } = renderSourceParameter({ parameter_name: "String", parameter_type: "string" })
    expect(screen.queryAllByLabelText(/String/).length).toBe(1)
    expect(screen.queryAllByDisplayValue(/https/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders a password parameter", async () => {
    const { container } = renderSourceParameter({ parameter_name: "Password", parameter_type: "password" })
    expect(screen.queryAllByLabelText(/Password/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders a date parameter", async () => {
    const { container } = renderSourceParameter({
        parameter_name: "Date",
        parameter_type: "date",
        parameter_value: "2021-10-10",
    })
    expect(screen.queryAllByLabelText(/Date/).length).toBe(1)
    expect(screen.queryAllByDisplayValue("10/10/2021").length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders a date parameter without date", async () => {
    const { container } = renderSourceParameter({
        parameter_name: "Date",
        parameter_type: "date",
        parameter_value: "",
    })
    expect(screen.queryAllByLabelText(/Date/).length).toBe(1)
    expect(screen.queryAllByPlaceholderText(/YYYY/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders an integer parameter", async () => {
    const { container } = renderSourceParameter({ parameter_name: "Integer", parameter_type: "integer" })
    expect(screen.queryAllByLabelText(/Integer/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("doesn't change an integer parameter with mouse wheel", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true })
    const { container } = renderSourceParameter({
        parameter_name: "Integer",
        parameter_type: "integer",
        parameter_value: "10",
    })
    fireEvent.wheel(screen.getByLabelText(/Integer/, { target: { scrollLeft: 500 } }))
    expect(fetch_server_api.fetch_server_api).not.toHaveBeenCalled()
    await expectNoAccessibilityViolations(container)
})

it("renders a single choice parameter", async () => {
    const { container } = renderSourceParameter({
        parameter_name: "Single choice",
        parameter_type: "single_choice",
        parameter_value: "option 1",
        parameter_values: ["option 1", "option 2"],
    })
    expect(screen.queryAllByLabelText(/Single choice/).length).toBe(1)
    expect(screen.queryAllByText(/option 1/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders a multiple choice parameter", async () => {
    const { container } = renderSourceParameter({
        parameter_name: "Multiple choice",
        parameter_type: "multiple_choice",
        parameter_value: ["option 1", "option 2"],
        parameter_values: ["option 1", "option 2", "option 3"],
    })
    expect(screen.queryAllByLabelText(/Multiple choice/).length).toBe(1)
    expect(screen.queryAllByText(/option 1/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders a multiple choice with addition parameter", async () => {
    const { container } = renderSourceParameter({
        parameter_name: "Multiple choice with addition",
        parameter_type: "multiple_choice_with_addition",
        parameter_value: ["option 1", "option 2"],
        placeholder: null,
    })
    expect(screen.queryAllByLabelText(/Multiple choice/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("renders nothing on unknown parameter type", async () => {
    const { container } = renderSourceParameter({ parameter_name: "Unknown", parameter_type: "unknown" })
    expect(screen.queryAllByText(/Unknown/).length).toBe(0)
    await expectNoAccessibilityViolations(container)
})

it("renders a help url", async () => {
    const { container } = renderSourceParameter({ help_url: "https://help" })
    expect(screen.queryAllByTitle(/Opens new window/)[0].closest("a").href).toBe("https://help/")
    await expectNoAccessibilityViolations(container)
})

it("renders a help text", async () => {
    const { container } = renderSourceParameter({ help: "Help text" })
    expect(screen.queryAllByText(/Help text/).length).toBe(1)
    await expectNoAccessibilityViolations(container)
})

it("changes the value", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true })
    const { container } = renderSourceParameter({})
    await userEvent.type(screen.getByLabelText(/URL/), "/new{Enter}")
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "source/source_uuid/parameter/key1", {
        key1: "https://test/new",
        edit_scope: "source",
    })
    await expectNoAccessibilityViolations(container)
})

it("changes the value via mass edit", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true })
    const { container } = renderSourceParameter({})
    fireEvent.click(screen.getByLabelText(/Edit scope/))
    fireEvent.click(screen.getByText(/Apply change to subject/))
    await userEvent.type(screen.getByLabelText(/URL/), "/new{Enter}")
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "source/source_uuid/parameter/key1", {
        key1: "https://test/new",
        edit_scope: "subject",
    })
    await expectNoAccessibilityViolations(container)
})

it("closes the mass edit menu", async () => {
    fetch_server_api.fetch_server_api = vi.fn().mockResolvedValue({ ok: true })
    const { container } = renderSourceParameter({})
    fireEvent.click(screen.getByLabelText(/Edit scope/))
    await userEvent.keyboard("{Escape}")
    expect(fetch_server_api.fetch_server_api).not.toHaveBeenCalled()
    await expectNoAccessibilityViolations(container)
})
