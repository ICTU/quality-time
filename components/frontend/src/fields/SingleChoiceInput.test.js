import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { Permissions } from '../context/Permissions';
import { SingleChoiceInput } from './SingleChoiceInput';

it('renders the value read only', () => {
    render(<SingleChoiceInput requiredPermissions={'testPermission'} value="hello" options={[{ text: "hello", value: "hello" }]} />);
    expect(screen.getByDisplayValue(/hello/)).not.toBe(null)
})

it('renders the editable value', () => {
    render(
        <Permissions.Provider value={false}>
            <SingleChoiceInput requiredPermissions={'testPermission'} value="hello" options={[{ text: "hello", value: "hello" }]} />
        </Permissions.Provider>
    )
    expect(screen.getByDisplayValue(/hello/)).not.toBe(null)
})

it('invokes the callback on a change', () => {
    let mockSetValue = jest.fn();
    render(
        <SingleChoiceInput
            value="hello"
            options={[{ text: "hello", value: "hello" }, { text: "hi", value: "hi" }]}
            set_value={mockSetValue}
        />
    )
    fireEvent.click(screen.getByText(/hi/))
    expect(mockSetValue).toHaveBeenCalledWith("hi");
})

it('does not invoke the callback when the value is not changed', () => {
    let mockSetValue = jest.fn();
    render(
        <SingleChoiceInput
            value="hello"
            options={[{ text: "hello", value: "hello" }, { text: "hi", value: "hi" }]}
            set_value={mockSetValue}
        />
    )
    fireEvent.click(screen.getAllByText(/hello/)[1])
    expect(mockSetValue).not.toHaveBeenCalled();
})

it('does sort by default', () => {
    render(
        <SingleChoiceInput
            value="b"
            options={[{ text: "option-b", value: "b" }, { text: "option-a", value: "a" }]}
        />
    )
    const options = screen.getAllByRole("option")
    expect(options[0]).toHaveTextContent("option-a")
    expect(options[1]).toHaveTextContent("option-b")
})

it('does not sort when told not to', () => {
    render(
        <SingleChoiceInput
            value="b"
            options={[{ text: "option-b", value: "b" }, { text: "option-a", value: "a" }]}
            sort={false}
        />
    )
    const options = screen.getAllByRole("option")
    expect(options[0]).toHaveTextContent("option-b")
    expect(options[1]).toHaveTextContent("option-a")
})

it('does sort when told to', () => {
    render(
        <SingleChoiceInput
            value="b"
            options={[{ text: "option-b", value: "b" }, { text: "option-a", value: "a" }]}
            sort={true}
        />
    )
    const options = screen.getAllByRole("option")
    expect(options[0]).toHaveTextContent("option-a")
    expect(options[1]).toHaveTextContent("option-b")
})
