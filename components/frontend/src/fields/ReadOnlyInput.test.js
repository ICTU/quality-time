import React from 'react';
import { render, screen } from '@testing-library/react';
import { ReadOnlyInput } from './ReadOnlyInput';

function renderReadOnlyInput({ value = "value", prefix = "", error = false, required = false } = {}) {
    return render(<ReadOnlyInput label={"Label"} value={value} prefix={prefix} required={required} error={error} />)
}

it("displays the value", () => {
    renderReadOnlyInput();
    expect(screen.queryByDisplayValue(/value/)).not.toBe(null)
});

it("displays the prefix", () => {
    renderReadOnlyInput({ prefix: "prefix" });
    expect(screen.queryByText(/prefix/)).not.toBe(null)
});

it("renders invalid on error", () => {
    renderReadOnlyInput({ error: true });
    expect(screen.queryByDisplayValue(/value/)).toBeInvalid()
});

it("renders invalid on required and empty", () => {
    renderReadOnlyInput({ required: true, value: "" });
    expect(screen.queryByDisplayValue("")).toBeInvalid()
});
