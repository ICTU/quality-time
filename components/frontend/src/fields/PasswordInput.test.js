import React from 'react';
import { render, screen } from '@testing-library/react';
import { PasswordInput } from './PasswordInput';

function renderPasswordInput({ placeholder = "", value = "" } = {}) {
    return render(<PasswordInput placeholder={placeholder} value={value} />)
}

it("hides the password", () => {
    renderPasswordInput({ value: "secret" });
    expect(screen.queryByDisplayValue(/secret/)).toBe(null)
});

it("shows the placeholder", () => {
    renderPasswordInput({ placeholder: "Enter password" });
    expect(screen.queryByPlaceholderText(/Enter password/)).not.toBe(null)
});
