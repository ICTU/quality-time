import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SourceParameter } from './SourceParameter';
import * as fetch_server_api from '../api/fetch_server_api';
import { EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';

jest.mock("../api/fetch_server_api.js")

const report = {
    "subjects": {
        "subject_uuid": {
            "metrics": {
                "metric_uuid": {
                    "sources": {
                        "source_uuid": {
                            "type": "source_type",
                            "parameters": { "key1": "" }
                        },
                        "other_source_uuid": {
                            "type": "source_type",
                            "parameters": { "key1": "value" }
                        },
                        "another_source_uuid": {
                            "type": "source_type",
                            "parameters": { "key1": ["value1", "value2"] }
                        },
                        "yet_another_source_uuid": { "type": "other_source_type" }
                    }
                }
            }
        }
    }
}

function renderSourceParameter(
    {
        help = null,
        help_url = null,
        index = 0,
        parameter_key = "key1",
        parameter_name = "URL",
        parameter_type = "url",
        parameter_value = "https://test",
        parameter_values = [],
        placeholder = "placeholder",
        warning = false,
    }
) {
    return render(
        <Permissions.Provider value={[EDIT_REPORT_PERMISSION]}>
            <SourceParameter
                help={help}
                help_url={help_url}
                index={index}
                parameter_key={parameter_key}
                parameter_name={parameter_name}
                parameter_type={parameter_type}
                parameter_value={parameter_value}
                parameter_values={parameter_values}
                placeholder={placeholder}
                report={report}
                source={{ "type": "source_type" }}
                source_uuid="source_uuid"
                warning={warning}
            />
        </Permissions.Provider>
    )
}

it('renders an url parameter', () => {
    renderSourceParameter({});
    expect(screen.queryAllByText(/URL/).length).toBe(1);
    expect(screen.queryAllByText(/placeholder/).length).toBe(1);
    expect(screen.getByDisplayValue(/https:\/\/test/)).toBeValid();
});

it('renders an url parameter with warning', () => {
    renderSourceParameter({ warning: true, index: 1 });
    expect(screen.queryAllByText(/URL/).length).toBe(1);
    expect(screen.queryAllByText(/placeholder/).length).toBe(1);
    expect(screen.getByRole("combobox")).toBeInvalid();
});

it('renders a string parameter', () => {
    renderSourceParameter({ parameter_name: "String", parameter_type: "string" });
    expect(screen.queryAllByText(/String/).length).toBe(1);
    expect(screen.queryAllByText(/placeholder/).length).toBe(1);
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
    renderSourceParameter({ parameter_name: "Unknown", parameter_type: "unknown" })
    expect(screen.queryAllByText(/Unknown/).length).toBe(0);
});

it('renders a help url', () => {
    renderSourceParameter({ help_url: "https://help" })
    expect(screen.queryByTitle(/Opens new window/).closest("a").href).toBe("https://help/")
});

it('renders a help text', async () => {
    renderSourceParameter({ help: "Help text" })
    await userEvent.hover(screen.queryByTestId("help-icon"))
    await waitFor(() => { expect(screen.queryAllByText(/Help text/).length).toBe(1) });
});

it('changes the value', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    renderSourceParameter({});
    await userEvent.type(screen.queryByText(/test/), "/new{Enter}")
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "source/source_uuid/parameter/key1", { key1: "https://test/new", edit_scope: "source" });
})

it('changes the value via mass edit', async () => {
    fetch_server_api.fetch_server_api = jest.fn().mockResolvedValue({ ok: true });
    renderSourceParameter({});
    await userEvent.click(screen.queryByText(/Apply change to subject/))
    await userEvent.type(screen.queryByText(/test/), "/new{Enter}")
    expect(fetch_server_api.fetch_server_api).toHaveBeenLastCalledWith("post", "source/source_uuid/parameter/key1", { key1: "https://test/new", edit_scope: "subject" });
})
