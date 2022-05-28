import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Permissions } from '../context/Permissions';
import { MultipleChoiceInput } from './MultipleChoiceInput';
import { dropdownOptions } from '../utils';

const defaultOptions = dropdownOptions(["hello", "again"]);

it('renders the value read only', () => {
    render(<MultipleChoiceInput requiredPermissions={["testPermission"]} value={["hello", "world"]} options={defaultOptions} />)
    expect(screen.getByDisplayValue(/hello, world/)).not.toBe(null)
})

it('renders an empty read only value', () => {
    render(<MultipleChoiceInput requiredPermissions={["testPermission"]} value={[]} options={defaultOptions} />)
    expect(screen.queryByDisplayValue(/hello/)).toBe(null)
})

it('renders in error state if a required value is missing', () => {
    render(<MultipleChoiceInput value={[]} required />)
    expect(screen.getByRole("combobox")).toBeInvalid()
})

it('does not render in error state if a required value is present', () => {
    render(<MultipleChoiceInput value={["check"]} options={[]} required />)
    expect(screen.getByRole("combobox")).toBeValid()
})

function renderMultipleChoiceInput(options=[], value=["hello"]) {
    let mockSetValue = jest.fn();
    render(
        <Permissions.Provider value={false}>
            <MultipleChoiceInput value={value} options={options} set_value={mockSetValue} allowAdditions={true} />
        </Permissions.Provider>
    )
    return mockSetValue
}

it('renders an editable value', () => {
    renderMultipleChoiceInput(defaultOptions)
    expect(screen.getByText(/hello/)).not.toBe(null)
})

it('renders a missing editable value', () => {
    renderMultipleChoiceInput(defaultOptions, [])
    expect(screen.queryByDisplayValue(/hello/)).toBe(null)
})

it('invokes the callback', () => {
    let mockSetValue = renderMultipleChoiceInput(defaultOptions)
    fireEvent.click(screen.getByText(/again/))
    expect(mockSetValue).toHaveBeenCalledWith(["hello", "again"]);
})

it('saves an uncommitted value on blur', async () => {
    let mockSetValue = renderMultipleChoiceInput()
    await userEvent.type(screen.getByDisplayValue(""), "new")
    await userEvent.tab()
    expect(mockSetValue).toHaveBeenCalledWith(["hello", "new"]);
})

it('does not save an uncommitted value on blur that is already in the list', async () => {
    let mockSetValue = renderMultipleChoiceInput()
    await userEvent.type(screen.getByDisplayValue(""), "hello")
    await userEvent.tab()
    expect(mockSetValue).not.toHaveBeenCalled();
})

it('does not save an uncommitted value on blur if there is none', async () => {
    let mockSetValue = renderMultipleChoiceInput()
    await userEvent.type(screen.getByDisplayValue(""), "x{Backspace}")
    await userEvent.tab()
    expect(mockSetValue).not.toHaveBeenCalled();
})
