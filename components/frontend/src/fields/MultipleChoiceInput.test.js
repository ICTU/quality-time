import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
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
