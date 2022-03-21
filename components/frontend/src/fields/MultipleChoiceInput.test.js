import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Permissions } from '../context/Permissions';
import { MultipleChoiceInput } from './MultipleChoiceInput';

it('renders the value read only', () => {
    render(<MultipleChoiceInput requiredPermissions={["testPermission"]} value={["hello", "world"]} options={["hello", "again"]} />)
    expect(screen.getByDisplayValue(/hello, world/)).not.toBe(null)
})

it('renders an empty read only value', () => {
    render(<MultipleChoiceInput requiredPermissions={["testPermission"]} value={[]} options={["hello", "again"]} />)
    expect(screen.queryByDisplayValue(/hello/)).toBe(null)
})

it('renders in error state if a required value is missing', () => {
    render(<MultipleChoiceInput value={[]} options={[]} required />)
    expect(screen.getByRole("combobox")).toBeInvalid()
})

it('does not render in error state if a required value is present', () => {
    render(<MultipleChoiceInput value={["check"]} options={[]} required />)
    expect(screen.getByRole("combobox")).toBeValid()
})

it('renders an editable value', () => {
    render(
        <Permissions.Provider value={false}>
            <MultipleChoiceInput value={["hello"]} options={["hello", "again"]} />
        </Permissions.Provider>
    )
    expect(screen.getByText(/hello/)).not.toBe(null)
})

it('renders a missing editable value', () => {
    render(
        <Permissions.Provider value={false}>
            <MultipleChoiceInput options={["hello", "again"]} />
        </Permissions.Provider>
    )
    expect(screen.queryByDisplayValue(/hello/)).toBe(null)
})

it('invokes the callback', () => {
    let mockSetValue = jest.fn();
    render(
        <Permissions.Provider value={false}>
            <MultipleChoiceInput value={["hello"]} options={["hello", "again"]} set_value={mockSetValue} />
        </Permissions.Provider>
    )
    fireEvent.click(screen.getByText(/again/))
    expect(mockSetValue).toHaveBeenCalledWith(["hello", "again"]);
})

it('does not add a value to the options twice', () => {
    let mockSetValue = jest.fn();
    render(
        <Permissions.Provider value={false}>
            <MultipleChoiceInput value={["hello"]} options={["hello", "again"]} set_value={mockSetValue} />
        </Permissions.Provider>
    )
    fireEvent.click(screen.getByText(/again/))
    expect(screen.getAllByText(/again/).length).toBe(1)
})

it('saves an uncommitted value on blur', () => {
    let mockSetValue = jest.fn();
    render(
        <Permissions.Provider value={false}>
            <MultipleChoiceInput value={["hello"]} options={[]} set_value={mockSetValue} />
            <input tabIndex="0" />
        </Permissions.Provider>
    )
    userEvent.type(screen.getAllByDisplayValue("")[0], "new")
    userEvent.tab()
    expect(mockSetValue).toHaveBeenCalledWith(["hello", "new"]);
})

it('does not save an uncommitted value on blur that is already in the list', () => {
    let mockSetValue = jest.fn();
    render(
        <Permissions.Provider value={false}>
            <MultipleChoiceInput value={["hello"]} options={[]} set_value={mockSetValue} />
            <input tabIndex="0" />
        </Permissions.Provider>
    )
    userEvent.type(screen.getAllByDisplayValue("")[0], "hello")
    userEvent.tab()
    expect(mockSetValue).not.toHaveBeenCalled();
})

it('does not save an uncommitted value on blur if there is none', () => {
    let mockSetValue = jest.fn();
    render(
        <Permissions.Provider value={false}>
            <MultipleChoiceInput value={["hello"]} options={[]} set_value={mockSetValue} />
            <input tabIndex="0" />
        </Permissions.Provider>
    )
    userEvent.type(screen.getAllByDisplayValue("")[0], "x{backspace}")
    userEvent.tab()
    expect(mockSetValue).not.toHaveBeenCalled();
})
