import { render, screen } from "@testing-library/react"

import { DataModel } from "../context/DataModel"
import { SourceParameters } from "./SourceParameters"

function renderSourceParameters({
    placeholder = "",
    type = "string",
    source_parameter_value = null,
    changed_param_keys = [],
}) {
    return render(
        <DataModel.Provider
            value={{
                metrics: { violations: {} },
                sources: {
                    source_type: {
                        parameters: {
                            parameter_key: {
                                default_value: "Default value",
                                placeholder: placeholder,
                                type: type,
                                name: "Parameter",
                                metrics: ["violations"],
                            },
                            other_parameter_key: {
                                default_value: "Other parameter default",
                                placeholder: "Other parameter placeholder",
                                type: type,
                                name: "Other parameter",
                                metrics: ["violations"],
                            },
                        },
                        parameter_layout: {
                            location: {
                                name: "Location parameters",
                                parameters: ["parameter_key"],
                            },
                            other: {
                                name: "Other parameters",
                                parameters: [],
                            },
                        },
                    },
                },
            }}
        >
            <SourceParameters
                report={{ subjects: {} }}
                metric={{ type: "violations" }}
                source={{
                    type: "source_type",
                    parameters: { parameter_key: source_parameter_value },
                }}
                changed_param_keys={changed_param_keys}
            />
        </DataModel.Provider>,
    )
}

it("renders a string parameter", () => {
    renderSourceParameters({})
    expect(screen.queryAllByLabelText(/Parameter/).length).toBe(1)
})

it("renders a string parameter with placeholder", () => {
    renderSourceParameters({ placeholder: "Placeholder" })
    expect(screen.queryAllByPlaceholderText(/Placeholder/).length).toBe(1)
})

it("renders a default value if the source parameter has no value", () => {
    renderSourceParameters({})
    expect(screen.queryAllByDisplayValue(/Default value/).length).toBe(1)
})

it("renders the source parameter value", () => {
    renderSourceParameters({ source_parameter_value: "Value" })
    expect(screen.queryAllByDisplayValue(/Value/).length).toBe(1)
})

it("does not render a warning if the url was reachable", () => {
    renderSourceParameters({ type: "url", changed_param_keys: ["other_parameter_key"] })
    expect(screen.getByDisplayValue(/Default value/)).toBeValid()
})

it("renders a warning if the url was not reachable", () => {
    renderSourceParameters({ type: "url", changed_param_keys: ["parameter_key"] })
    expect(screen.getByDisplayValue(/Default value/)).toBeInvalid()
})

it("renders parameter groups", () => {
    renderSourceParameters({})
    expect(screen.queryAllByText(/Location parameters/).length).toBe(1)
    expect(screen.queryAllByText(/Other parameters/).length).toBe(1)
})

it("renders ungrouped parameters in the group without explicitly listed parameters", () => {
    renderSourceParameters({})
    expect(screen.queryAllByLabelText(/Other parameter/).length).toBe(1)
})
