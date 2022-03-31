import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Permissions } from '../context/Permissions';
import { StringInput } from './StringInput';

function renderStringInput(set_value) {
    return render(
        <Permissions.Provider value={false}>
            <StringInput
                options={["Option 1", "Option 2"]}
                set_value={set_value}
                value="Option 1"
            />
        </Permissions.Provider>
    )
}

it('renders the value of the input', () => {
    renderStringInput();
    expect(screen.getByDisplayValue(/Option 1/)).not.toBe(null)
});

it('renders a missing value', () => {
    render(<StringInput options={["Option 1", "Option 2"]} />)
    expect(screen.queryByDisplayValue(/Option/)).toBe(null)
});

it('invokes the callback on change', async () => {
    const mockCallback = jest.fn();
    renderStringInput(mockCallback);
    await userEvent.type(screen.getByDisplayValue(/Option 1/), 'Option 2{Enter}', {initialSelectionStart: 0, initialSelectionEnd: 8})
    expect(screen.getByDisplayValue(/Option 2/)).not.toBe(null)
    expect(mockCallback).toHaveBeenCalledWith("Option 2")
});

it('invokes the callback on add', async () => {
    const mockCallback = jest.fn();
    renderStringInput(mockCallback);
    await userEvent.type(screen.getByDisplayValue(/Option 1/), 'Option 3{Enter}', {initialSelectionStart: 0, initialSelectionEnd: 8})
    expect(screen.getByDisplayValue(/Option 3/)).not.toBe(null)
    expect(mockCallback).toHaveBeenCalledWith("Option 3")
});

it('does not invoke the callback when the new value equals the old value', async () => {
    const mockCallback = jest.fn();
    renderStringInput(mockCallback);
    await userEvent.type(screen.getByDisplayValue(/Option 1/), 'Option 1{Enter}', {initialSelectionStart: 0, initialSelectionEnd: 8})
    expect(screen.getByDisplayValue(/Option 1/)).not.toBe(null)
    expect(mockCallback).not.toHaveBeenCalled()
});

it('works without options', async () => {
    const mockCallback = jest.fn();
    renderStringInput(mockCallback);
    render(<StringInput set_value={mockCallback} />)
    await userEvent.type(screen.getByDisplayValue(""), 'New value{Enter}')
    expect(screen.getByDisplayValue(/New value/)).not.toBe(null)
    expect(mockCallback).toHaveBeenCalledWith("New value")
});

it('shows an error for required empty fields', () => {
    render(<StringInput options={["Option 1", "Option 2"]} required />)
    expect(screen.getByRole("combobox")).toBeInvalid()
});

it('does not show an error for required non-empty fields', () => {
    render(<StringInput options={["Option 1", "Option 2"]} value="Hello" required />)
    expect(screen.getByRole("combobox")).toBeValid()
});

it('does not show an error for non-required empty fields', () => {
    render(<StringInput options={["Option 1", "Option 2"]} value="" />)
    expect(screen.getByRole("combobox")).toBeValid()
});

it('does not show an error for non-required non-empty fields', () => {
    render(<StringInput options={["Option 1", "Option 2"]} value="Hello" />)
    expect(screen.getByRole("combobox")).toBeValid()
});

it('shows an error', () => {
    render(<StringInput options={["Option 1", "Option 2"]} value="Hello" error />)
    expect(screen.getByRole("combobox")).toBeInvalid()
});

it('shows a warning', () => {
    render(<StringInput options={["Option 1", "Option 2"]} value="Hello" warning />)
    expect(screen.getByRole("combobox")).toBeInvalid()
});
