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

it('invokes the callback on change', () => {
    const mockCallback = jest.fn();
    renderStringInput(mockCallback);
    userEvent.type(screen.getByDisplayValue(/Option 1/), '{selectall}Option 2{enter}')
    expect(screen.getByDisplayValue(/Option 2/)).not.toBe(null)
    expect(mockCallback).toHaveBeenCalledWith("Option 2")
});

it('invokes the callback on add', () => {
    const mockCallback = jest.fn();
    renderStringInput(mockCallback);
    userEvent.type(screen.getByDisplayValue(/Option 1/), '{selectall}Option 3{enter}')
    expect(screen.getByDisplayValue(/Option 3/)).not.toBe(null)
    expect(mockCallback).toHaveBeenCalledWith("Option 3")
});
