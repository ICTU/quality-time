import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { IntegerInput } from './IntegerInput';

it('renders the value read only', () => {
    render(<IntegerInput requiredPermissions={['testPermission']} value="42" />)
    expect(screen.queryAllByDisplayValue(/42/).length).toBe(1);
});

it('renders and edits the value', async () => {
    let set_value = jest.fn();
    render(<IntegerInput value="42" set_value={set_value} />)
    await userEvent.type(screen.getByDisplayValue(/42/), "123{Enter}", {initialSelectionStart: 0, initialSelectionEnd: 2})
    expect(screen.queryAllByDisplayValue(/123/).length).toBe(1);
    expect(set_value).toHaveBeenCalledWith("123");
});

it('submits the changed value on blur', async () => {
    let set_value = jest.fn();
    render(
        <>
            <IntegerInput value="42" set_value={set_value} />
            <IntegerInput value="222"/>
        </>
    )
    await userEvent.type(screen.getByDisplayValue(/42/), "123", {initialSelectionStart: 0, initialSelectionEnd: 2})
    screen.getByDisplayValue(/222/).focus();  // blur
    expect(screen.queryAllByDisplayValue(/123/).length).toBe(1);
    expect(set_value).toHaveBeenCalledWith("123");
});

it('does not submit an unchanged value', async () => {
    let set_value = jest.fn();
    render(<IntegerInput value="42" set_value={set_value} />)
    await userEvent.type(screen.getByDisplayValue(/42/), "{Enter}")
    expect(screen.queryAllByDisplayValue(/42/).length).toBe(1);
    expect(set_value).not.toHaveBeenCalled();
});

it('does not submit a value that is too small', async () => {
    let set_value = jest.fn();
    render(<IntegerInput value="-1" min={0} set_value={set_value} />)
    await userEvent.type(screen.getByDisplayValue(/-1/), "{Enter}")
    expect(screen.queryAllByDisplayValue(/-1/).length).toBe(1);
    expect(set_value).not.toHaveBeenCalled();
});

it('does not accept an invalid value', async () => {
    let set_value = jest.fn();
    render(<IntegerInput value="42" set_value={set_value} />)
    await userEvent.type(screen.getByDisplayValue(/42/), "abc{Enter}")
    expect(set_value).not.toHaveBeenCalled();
});

it('undoes the change on escape', async () => {
    let set_value = jest.fn();
    render(<IntegerInput value="42" set_value={set_value} />)
    await userEvent.type(screen.getByDisplayValue(/42/), "24{escape}")
    expect(screen.queryAllByDisplayValue(/42/).length).toBe(1);
    expect(set_value).not.toHaveBeenCalled();
});

it('renders values less than the minimum as invalid', () => {
    render(<IntegerInput value="-42" min="0" />)
    expect(screen.getByDisplayValue(/-42/)).toBeInvalid()
});

it('renders values more than the minimum as valid', () => {
    render(<IntegerInput value="42" min="0" />)
    expect(screen.getByDisplayValue(/42/)).toBeValid()
});

it('renders values more than the maximum as invalid', () => {
    render(<IntegerInput value="42" max="10" />)
    expect(screen.getByDisplayValue(/42/)).toBeInvalid()
});

it('renders values less than the maximum as valid', () => {
    render(<IntegerInput value="42" max="100" />)
    expect(screen.getByDisplayValue(/42/)).toBeValid()
});
