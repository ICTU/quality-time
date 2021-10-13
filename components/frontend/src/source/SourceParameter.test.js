import React from 'react';
import { render, screen } from '@testing-library/react';
import { SourceParameter } from './SourceParameter';

const report = { "subjects": [{ "metrics": [{ "sources": [{ "type": "x", "parameters": { "key": "b" } }] }] }] }

function renderSourceParameter(
    {
        parameter_name = "URL",
        parameter_type = "url",
        parameter_value = "https://test",
        parameter_values = [],
        placeholder = "placeholder",
        warning = false,
    }
) {
    return render(
        <SourceParameter
            parameter_name={parameter_name}
            parameter_type={parameter_type}
            parameter_value={parameter_value}
            parameter_values={parameter_values}
            placeholder={placeholder}
            report={report}
            source={{ "type": "x" }}
            warning={warning}
        />
    )
}

it('renders an url parameter', () => {
    renderSourceParameter({});
    expect(screen.queryAllByText(/URL/).length).toBe(1);
    expect(screen.queryAllByPlaceholderText(/placeholder/).length).toBe(1);
    expect(screen.getByDisplayValue(/https:\/\/test/)).toBeValid();
});

it('renders an url parameter with warning', () => {
    renderSourceParameter({ warning: true });
    expect(screen.queryAllByText(/URL/).length).toBe(1);
    expect(screen.queryAllByPlaceholderText(/placeholder/).length).toBe(1);
    expect(screen.getByDisplayValue(/https:\/\/test/)).toBeInvalid();
});

it('renders a string parameter', () => {
    renderSourceParameter({ parameter_name: "String", parameter_type: "string" });
    expect(screen.queryAllByText(/String/).length).toBe(1);
    expect(screen.queryAllByPlaceholderText(/placeholder/).length).toBe(1);
});

it('renders a password parameter', () => {
    renderSourceParameter({ parameter_name: "Password", parameter_type: "password" });
    expect(screen.queryAllByText(/Password/).length).toBe(1);
    expect(screen.queryAllByPlaceholderText(/placeholder/).length).toBe(1);
});

it('renders a date parameter', () => {
    renderSourceParameter({ parameter_name: "Date", parameter_type: "date", parameter_value: "2021-10-10" });
    expect(screen.queryAllByText(/Date/).length).toBe(1);
    expect(screen.queryAllByDisplayValue(/2021\-10\-10/).length).toBe(1);
});

it('renders an integer parameter', () => {
    renderSourceParameter({ parameter_name: "Integer", parameter_type: "integer" });
    expect(screen.queryAllByText(/Integer/).length).toBe(1);
    expect(screen.queryAllByPlaceholderText(/placeholder/).length).toBe(1);
});

it('renders a single choice parameter', () => {
    renderSourceParameter(
        {
            parameter_name: "Single choice",
            parameter_type: "single_choice",
            parameter_value: "option 1",
            parameter_values: ["option 1", "option 2"],
        }
    );
    expect(screen.queryAllByText(/Single choice/).length).toBe(1);
    expect(screen.queryAllByText(/option 1/).length).toBe(2);
});

it('renders a multiple choice parameter', () => {
    renderSourceParameter(
        {
            parameter_name: "Multiple choice",
            parameter_type: "multiple_choice",
            parameter_value: ["option 1", "option 2"],
            parameter_values: ["option 1", "option 2", "option 3"],
        }
    );
    expect(screen.queryAllByText(/Multiple choice/).length).toBe(1);
    expect(screen.queryAllByText(/option 1/).length).toBe(1);
});

it('renders a multiple choice with addition parameter', () => {
    renderSourceParameter(
        {
            parameter_name: "Multiple choice with addition",
            parameter_type: "multiple_choice_with_addition",
            parameter_value: ["option 1", "option 2"],
            placeholder: null,
        }
    );
    expect(screen.queryAllByText(/Multiple choice/).length).toBe(1);
});

it('renders nothing on unknown parameter type', () => {
    renderSourceParameter({parameter_name: "Unknown", parameter_type: "unknown"})
    expect(screen.queryAllByText(/Unknown/).length).toBe(0);
})
