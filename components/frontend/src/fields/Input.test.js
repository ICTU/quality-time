import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Input } from './Input';

it('changes the value', async () => {
    const mockCallback = jest.fn();
    render(<Input value="Hello" set_value={mockCallback} />)
    await userEvent.type(screen.getByDisplayValue(/Hello/), 'Bye{Enter}', {initialSelectionStart: 0, initialSelectionEnd: 5})
    expect(screen.getByDisplayValue(/Bye/)).not.toBe(null)
    expect(mockCallback).toHaveBeenCalledWith("Bye")
});

it('changes the value when blurred', async () => {
    const mockCallback = jest.fn();
    render(<><Input value="Hello" set_value={mockCallback} /><Input value="Bye" /></>)
    await userEvent.type(screen.getByDisplayValue(/Hello/), 'Ciao', {initialSelectionStart: 0, initialSelectionEnd: 5})
    screen.getByDisplayValue(/Bye/).focus();  // blur
    expect(mockCallback).toHaveBeenCalledWith("Ciao");
});

it('does not submit the value when it is unchanged', async () => {
    const mockCallback = jest.fn();
    render(<Input value="Hello" set_value={mockCallback} />)
    await userEvent.type(screen.getByDisplayValue(/Hello/), 'Hello{Enter}', {initialSelectionStart: 0, initialSelectionEnd: 5})
    expect(screen.getByDisplayValue(/Hello/)).not.toBe(null)
    expect(mockCallback).not.toHaveBeenCalled()
});

it('renders the initial value on escape and does not submit', async () => {
    const mockCallback = jest.fn();
    render(<Input value="Hello" set_value={mockCallback} />)
    await userEvent.type(screen.getByDisplayValue(/Hello/), 'Bye{Escape}')
    expect(screen.getByDisplayValue(/Hello/)).not.toBe(null)
    expect(mockCallback).not.toHaveBeenCalled()
});

it('shows an error for required empty fields', () => {
    const { container } = render(<Input value="" required />)
    expect(container.getElementsByTagName("input")[0]).toBeInvalid()
});

it('does not show an error for required non-empty fields', () => {
    const { container } = render(<Input value="Hello" required />)
    expect(container.getElementsByTagName("input")[0]).toBeValid()
});

it('does not show an error for non-required empty fields', () => {
    const { container } = render(<Input value="" />)
    expect(container.getElementsByTagName("input")[0]).toBeValid()
});

it('renders in error state if the warning props is true', () => {
    const { container } = render(<Input value="" warning />)
    expect(container.getElementsByTagName("input")[0]).toBeInvalid()
});
