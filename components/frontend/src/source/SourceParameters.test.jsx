import { render, screen } from "@testing-library/react"

import { DataModelContext } from "../context/DataModel"
import { expectDisplayValue, expectLabelText, expectNoAccessibilityViolations, expectText } from "../testUtils"
import { SourceParameters } from "./SourceParameters"

function renderSourceParameters({
    fieldWithUrlAvailabilityError = {},
    defaultValue = "Default value",
    mandatory = false,
    placeholder = "",
    type = "string",
    sourceParameterValue = null,
}) {
    return render(
        <DataModelContext
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
                fieldWithUrlAvailabilityError={fieldWithUrlAvailabilityError}
                report={{ subjects: {} }}
                metric={{ type: "violations" }}
                source={{
                    type: "source_type",
                    parameters: { parameter_key: sourceParameterValue },
                }}
                sourceUuid="source_uuid"
            />
        </DataModelContext>,
    )
}

it("has no accessibility violations", async () => {
    const { container } = renderSourceParameters({})
    await expectNoAccessibilityViolations(container)
})

it("renders a string parameter", async () => {
    renderSourceParameters({})
    expectLabelText(/Parameter/)
})

it("renders a string parameter with placeholder", async () => {
    renderSourceParameters({ placeholder: "Placeholder" })
    expect(screen.queryAllByPlaceholderText(/Placeholder/).length).toBe(1)
})

it("renders a default value if the source parameter has no value", async () => {
    renderSourceParameters({})
    expectDisplayValue(/Default value/)
})

it("renders the source parameter value", async () => {
    renderSourceParameters({ sourceParameterValue: "Value" })
    expectDisplayValue(/Value/)
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
    renderSourceParameters({
        type: "url",
        fieldWithUrlAvailabilityError: { parameter_key: "other_parameter_key", source_uuid: "source_uuid" },
    })
    expect(screen.getByDisplayValue(/Default value/)).toBeValid()
})

it("renders a warning if the url was not reachable", async () => {
    renderSourceParameters({
        type: "url",
        fieldWithUrlAvailabilityError: { parameter_key: "parameter_key", source_uuid: "source_uuid" },
    })
    expect(screen.getByDisplayValue(/Default value/)).toBeInvalid()
})

it("renders parameter groups", async () => {
    renderSourceParameters({})
    expectText(/Location parameters/)
    expectText(/Other parameters/)
})

it("renders ungrouped parameters in the group without explicitly listed parameters", async () => {
    renderSourceParameters({})
    expectLabelText(/Other parameter/)
})
