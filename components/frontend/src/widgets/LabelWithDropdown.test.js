import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { LabelWithDropdown } from './LabelWithDropdown';

it("shows the label", () => {
    render(<LabelWithDropdown label="Hello" />)
    expect(screen.getByText(/Hello/)).not.toBe(null)
})

it("can be colored", () => {
    render(<LabelWithDropdown label="Hello" color="red" options={[{key: "1", value: "1", text: "Option 1", description: "1", label: { color: "red"}}]} />)
    expect(screen.getByRole("listbox")).toHaveAttribute("color", "red")
})

it("has default color black", () => {
    render(<LabelWithDropdown label="Hello" options={[{key: "1", value: "1", text: "Option 1", description: "1", label: { color: "red"}}]} />)
    expect(screen.getByRole("listbox")).not.toHaveAttribute("color")
})

it("changes the option", () => {
    const mockCallback = jest.fn()
    render(
        <LabelWithDropdown
            label="Hello"
            onChange={mockCallback}
            options={[{key: "1", value: "1", text: "Option 1"}, {key: "2", value: "2", text: "Option 2"}]}
            value="1"
        />
    )
    fireEvent.click(screen.getByText(/Option 2/))
    expect(mockCallback).toHaveBeenCalled()
})

it("opens the dropdown when clicking the current option", () => {
    const mockCallback = jest.fn()
    render(
        <LabelWithDropdown
            label="Hello"
            onChange={mockCallback}
            options={[{key: "1", value: "1", text: "Option 1"}, {key: "2", value: "2", text: "Option 2"}]}
            value="1"
        />
    )
    expect(screen.getByRole("listbox")).toHaveAttribute("aria-expanded", "false")
    fireEvent.click(screen.getAllByText(/Option 1/)[0])
    expect(screen.getByRole("listbox")).toHaveAttribute("aria-expanded", "true")
})
