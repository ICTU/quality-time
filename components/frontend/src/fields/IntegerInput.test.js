import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Permissions } from '../context/Permissions';
import { IntegerInput } from './IntegerInput';

it('renders the value read only', () => {
    render(<IntegerInput requiredPermissions={['testPermission']} value="42" />)
    expect(screen.queryAllByDisplayValue(/42/).length).toBe(1);
});

it('renders and edits the value', () => {
    let set_value = jest.fn();
    render(<Permissions.Provider value={false}><IntegerInput value="42" set_value={set_value} /></Permissions.Provider>)
    userEvent.type(screen.getByDisplayValue(/42/), "{selectall}123{enter}")
    expect(screen.queryAllByDisplayValue(/123/).length).toBe(1);
    expect(set_value).toHaveBeenCalledWith("123");
});

it('submits the changed value on blur', () => {
    let set_value = jest.fn();
    render(
        <Permissions.Provider value={false}>
            <IntegerInput value="42" set_value={set_value} />
            <IntegerInput value="222"/>
        </Permissions.Provider>
    )
    userEvent.type(screen.getByDisplayValue(/42/), "{selectall}123")
    screen.getByDisplayValue(/222/).focus();  // blur
    expect(screen.queryAllByDisplayValue(/123/).length).toBe(1);
    expect(set_value).toHaveBeenCalledWith("123");
});

it('does not submit an unchanged value', () => {
    let set_value = jest.fn();
    render(<Permissions.Provider value={false}><IntegerInput value="42" set_value={set_value} /></Permissions.Provider>)
    userEvent.type(screen.getByDisplayValue(/42/), "{selectall}42{enter}")
    expect(screen.queryAllByDisplayValue(/42/).length).toBe(1);
    expect(set_value).not.toHaveBeenCalled();
});

it('does not submit a value that is too small', () => {
    let set_value = jest.fn();
    render(<Permissions.Provider value={false}><IntegerInput value="42" min="0" set_value={set_value} /></Permissions.Provider>)
    userEvent.type(screen.getByDisplayValue(/42/), "{selectall}-1{enter}")
    expect(set_value).not.toHaveBeenCalled();
});

it('does not accept an invalid value', () => {
    let set_value = jest.fn();
    render(<Permissions.Provider value={false}><IntegerInput value="42" set_value={set_value} /></Permissions.Provider>)
    userEvent.type(screen.getByDisplayValue(/42/), "{selectall}abc{enter}")
    expect(set_value).not.toHaveBeenCalled();
});

it('undoes the change on escape', () => {
    let set_value = jest.fn();
    render(<Permissions.Provider value={false}><IntegerInput value="42" set_value={set_value} /></Permissions.Provider>)
    userEvent.type(screen.getByDisplayValue(/42/), "{selectall}42{escape}")
    expect(screen.queryAllByDisplayValue(/42/).length).toBe(1);
    expect(set_value).not.toHaveBeenCalled();
});

it('renders values less than the minimum as invalid', () => {
    render(<Permissions.Provider value={false}><IntegerInput value="-42" min="0" /></Permissions.Provider>)
    expect(screen.getByDisplayValue(/-42/)).toBeInvalid()
});

it('renders values more than the minimum as valid', () => {
    render(<Permissions.Provider value={false}><IntegerInput value="42" min="0" /></Permissions.Provider>)
    expect(screen.getByDisplayValue(/42/)).toBeValid()
});

it('renders values more than the maximum as invalid', () => {
    render(<Permissions.Provider value={false}><IntegerInput value="42" max="10" /></Permissions.Provider>)
    expect(screen.getByDisplayValue(/42/)).toBeInvalid()
});

it('renders values less than the maximum as valid', () => {
    render(<Permissions.Provider value={false}><IntegerInput value="42" max="100" /></Permissions.Provider>)
    expect(screen.getByDisplayValue(/42/)).toBeValid()
});
