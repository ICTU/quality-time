import { render, screen } from "@testing-library/react"

import { DataModel } from "../context/DataModel"
import { expectNoAccessibilityViolations, expectText } from "../testUtils"
import { SourceParameters } from "./SourceParameters"

function renderSourceParameters({
    changedParamKeys = [],
    defaultValue = "Default value",
    mandatory = false,
    placeholder = "",
    type = "string",
    sourceParameterValue = null,
}) {
    return render(
        <DataModel.Provider
            value={{
                metrics: { violations: {} },
                sources: {
                    source_type: {
                        parameters: {
                            parameter_key: {
                                default_value: defaultValue,
                                mandatory: mandatory,
                                metrics: ["violations"],
                                name: "Parameter",
                                placeholder: placeholder,
                                type: type,
                            },
                            other_parameter_key: {
                                default_value: "Other parameter default",
                                metrics: ["violations"],
                                name: "Other parameter",
                                placeholder: "Other parameter placeholder",
                                type: type,
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
                    parameters: { parameter_key: sourceParameterValue },
                }}
                changedParamKeys={changedParamKeys}
            />
        </DataModel.Provider>,
    )
}

it("has no accessibility violations", async () => {
    const { container } = renderSourceParameters({})
    await expectNoAccessibilityViolations(container)
})

it("renders a string parameter", async () => {
    renderSourceParameters({})
    expect(screen.queryAllByLabelText(/Parameter/).length).toBe(1)
})

it("renders a string parameter with placeholder", async () => {
    renderSourceParameters({ placeholder: "Placeholder" })
    expect(screen.queryAllByPlaceholderText(/Placeholder/).length).toBe(1)
})

it("renders a default value if the source parameter has no value", async () => {
    renderSourceParameters({})
    expect(screen.queryAllByDisplayValue(/Default value/).length).toBe(1)
})

it("renders the source parameter value", async () => {
    renderSourceParameters({ sourceParameterValue: "Value" })
    expect(screen.queryAllByDisplayValue(/Value/).length).toBe(1)
})

it("does not render a warning if a mandatory parameter has a value", async () => {
    renderSourceParameters({ defaultValue: "Value", mandatory: true })
    expect(screen.getByDisplayValue(/Value/)).toBeValid()
})

it("renders a warning if a mandatory parameter has no value", async () => {
    renderSourceParameters({ defaultValue: "", placeholder: "Placeholder", mandatory: true })
    expect(screen.getByPlaceholderText(/Placeholder/)).toBeInvalid()
})

it("does not render a warning if the url was reachable", async () => {
    renderSourceParameters({ type: "url", changedParamKeys: ["other_parameter_key"] })
    expect(screen.getByDisplayValue(/Default value/)).toBeValid()
})

it("renders a warning if the url was not reachable", async () => {
    renderSourceParameters({ type: "url", changedParamKeys: ["parameter_key"] })
    expect(screen.getByDisplayValue(/Default value/)).toBeInvalid()
})

it("renders parameter groups", async () => {
    renderSourceParameters({})
    expectText(/Location parameters/)
    expectText(/Other parameters/)
})

it("renders ungrouped parameters in the group without explicitly listed parameters", async () => {
    renderSourceParameters({})
    expect(screen.queryAllByLabelText(/Other parameter/).length).toBe(1)
})
