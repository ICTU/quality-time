import React from 'react';
import { render, screen } from '@testing-library/react';
import { ReadOnlyInput } from './ReadOnlyInput';

function renderReadOnlyInput({ value = "value", prefix = "" } = {}) {
    return render(<ReadOnlyInput label={"Label"} value={value} prefix={prefix} />)
}

it("displays the value", () => {
    renderReadOnlyInput();
    expect(screen.queryByDisplayValue(/value/)).not.toBe(null)
});

it("displays the prefix", () => {
    renderReadOnlyInput({ prefix: "prefix" });
    expect(screen.queryByText(/prefix/)).not.toBe(null)
});