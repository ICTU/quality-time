import React from 'react';
import { render, screen } from '@testing-library/react';
import { DataModel } from '../context/DataModel';
import { SourceParameters } from './SourceParameters';

function renderSourceParameters({placeholder = "", type = "string", source_parameter_value = null, changed_param_keys = []}) {
    return render(
        <DataModel.Provider value={
            {
                sources: {
                    source_type: {
                        parameters: {
                            parameter_key: {
                                default_value: "Default value",
                                placeholder: placeholder,
                                type: type,
                                name: "Parameter",
                                metrics: ["violations"]
                            }
                        }
                    }
                }
            }
        }>
            <SourceParameters
                report={{subjects: {}}}
                metric_type="violations"
                source={{ type: "source_type", parameters: {parameter_key: source_parameter_value} }}
                changed_param_keys={changed_param_keys}
            />
        </DataModel.Provider>
    )
}

it("renders a string parameter", () => {
    renderSourceParameters({});
    expect(screen.queryAllByText(/Parameter/).length).toBe(1);
});

it("renders a string parameter with placeholder", () => {
    renderSourceParameters({placeholder: "Placeholder"});
    expect(screen.queryAllByPlaceholderText(/Placeholder/).length).toBe(1);
});

it("renders a default value if the source parameter has no value", () => {
    renderSourceParameters({});
    expect(screen.queryAllByDisplayValue(/Default value/).length).toBe(1);
});

it("renders the source parameter value", () => {
    renderSourceParameters({source_parameter_value: "Value"});
    expect(screen.queryAllByDisplayValue(/Value/).length).toBe(1);
});

it("renders a warning if the url was not reachable", () => {
    renderSourceParameters({type: "url", changed_param_keys: ["parameter_key"]});
    expect(screen.getByDisplayValue(/Default value/)).toBeInvalid();
});
