import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TextInput } from './TextInput';

it('renders the value read only', () => {
    render(<TextInput requiredPermissions={['test']} value="Hello" />)
    expect(screen.queryByText("Hello")).not.toBe(null)
});

it('changes the value', () =>{
    const mockCallback = jest.fn();
    render(<TextInput value="Hello" set_value={mockCallback} />);
    userEvent.type(screen.getByText(/Hello/), '{selectall}Bye{shift}{enter}')
    expect(screen.getByText(/Bye/)).not.toBe(null)
    expect(mockCallback).toHaveBeenCalledWith("Bye")
})

it('does not invoke the callback if the value is unchanged', () =>{
    const mockCallback = jest.fn();
    render(<TextInput value="Hello" set_value={mockCallback} />);
    userEvent.type(screen.getByText(/Hello/), '{selectall}Hello{shift}{enter}')
    expect(screen.getByText(/Hello/)).not.toBe(null)
    expect(mockCallback).not.toHaveBeenCalled()
})

it('resets the value on escape', () =>{
    const mockCallback = jest.fn();
    render(<TextInput value="Hello" set_value={mockCallback} />);
    userEvent.type(screen.getByText(/Hello/), '{selectall}Revert{escape}')
    expect(screen.getByText(/Hello/)).not.toBe(null)
    expect(mockCallback).not.toHaveBeenCalled()
})
