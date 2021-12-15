import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Input } from './Input';

it('changes the value', () => {
    const mockCallback = jest.fn();
    render(<Input value="Hello" set_value={mockCallback} />)
    userEvent.type(screen.getByDisplayValue(/Hello/), '{selectall}Bye{enter}')
    expect(screen.getByDisplayValue(/Bye/)).not.toBe(null)
    expect(mockCallback).toHaveBeenCalledWith("Bye")
});

it('changes the value when blurred', () => {
    const mockCallback = jest.fn();
    render(<><Input value="Hello" set_value={mockCallback} /><Input value="Bye" /></>)
    userEvent.type(screen.getByDisplayValue(/Hello/), '{selectall}Ciao')
    screen.getByDisplayValue(/Bye/).focus();  // blur
    expect(mockCallback).toHaveBeenCalledWith("Ciao");
});

it('does not submit the value when it is unchanged', () => {
    const mockCallback = jest.fn();
    render(<Input value="Hello" set_value={mockCallback} />)
    userEvent.type(screen.getByDisplayValue(/Hello/), '{selectall}Hello{enter}')
    expect(screen.getByDisplayValue(/Hello/)).not.toBe(null)
    expect(mockCallback).not.toHaveBeenCalled()
});

it('renders the initial value on escape and does not submit', () => {
    const mockCallback = jest.fn();
    render(<Input value="Hello" set_value={mockCallback} />)
    userEvent.type(screen.getByDisplayValue(/Hello/), '{selectall}Bye{escape}')
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
