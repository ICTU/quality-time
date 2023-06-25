import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { IntegerInput } from './IntegerInput';

it('renders the value read only', () => {
    render(<IntegerInput requiredPermissions={['testPermission']} value="42" />)
    expect(screen.queryAllByDisplayValue(/42/).length).toBe(1);
});

it('renders and edits the value', async () => {
    let setValue = jest.fn();
    render(<IntegerInput value="42" set_value={setValue} />)
    await userEvent.type(screen.getByDisplayValue(/42/), "123{Enter}", {initialSelectionStart: 0, initialSelectionEnd: 2})
    expect(screen.queryAllByDisplayValue(/123/).length).toBe(1);
    expect(setValue).toHaveBeenCalledWith("123");
});

it('submits the changed value on blur', async () => {
    let setValue = jest.fn();
    render(
        <>
            <IntegerInput value="42" set_value={setValue} />
            <IntegerInput value="222"/>
        </>
    )
    await userEvent.type(screen.getByDisplayValue(/42/), "123", {initialSelectionStart: 0, initialSelectionEnd: 2})
    screen.getByDisplayValue(/222/).focus();  // blur
    expect(screen.queryAllByDisplayValue(/123/).length).toBe(1);
    expect(setValue).toHaveBeenCalledWith("123");
});

it('does not submit an unchanged value', async () => {
    let setValue = jest.fn();
    render(<IntegerInput value="42" set_value={setValue} />)
    await userEvent.type(screen.getByDisplayValue(/42/), "{Enter}")
    expect(screen.queryAllByDisplayValue(/42/).length).toBe(1);
    expect(setValue).not.toHaveBeenCalled();
});

it('does not submit a value that is too small', async () => {
    let setValue = jest.fn();
    render(<IntegerInput value="5" min={10} set_value={setValue} />)
    await userEvent.type(screen.getByDisplayValue(/5/), "{Enter}")
    expect(screen.queryAllByDisplayValue(/5/).length).toBe(1);
    expect(setValue).not.toHaveBeenCalled();
});

it('has a default mininum of zero', async () => {
    let setValue = jest.fn();
    render(<IntegerInput value="-1" set_value={setValue} />)
    await userEvent.type(screen.getByDisplayValue(/-1/), "{Enter}")
    expect(screen.queryAllByDisplayValue(/-1/).length).toBe(1);
    expect(setValue).not.toHaveBeenCalled();
});

it('does not accept an invalid value', async () => {
    let setValue = jest.fn();
    render(<IntegerInput value="42" set_value={setValue} />)
    await userEvent.type(screen.getByDisplayValue(/42/), "abc{Enter}")
    expect(setValue).not.toHaveBeenCalled();
});

it('does not accept an empty value', async () => {
    let setValue = jest.fn();
    render(<IntegerInput value="42" set_value={setValue} />)
    await userEvent.type(screen.getByDisplayValue(/42/), "{selectall}{backspace}{backspace}{enter}")
    // The second backspace does not delete the 4 because input cannot be empty
    expect(setValue).toHaveBeenCalledWith("4");
});

it('accepts an empty value when allowed', async () => {
    let setValue = jest.fn();
    render(<IntegerInput allowEmpty value="42" set_value={setValue} />)
    await userEvent.type(screen.getByDisplayValue(/42/), "{selectall}{backspace}{backspace}{enter}")
    expect(setValue).toHaveBeenCalledWith("");
});

it('undoes the change on escape', async () => {
    let setValue = jest.fn();
    render(<IntegerInput value="42" set_value={setValue} />)
    await userEvent.type(screen.getByDisplayValue(/42/), "24{escape}")
    expect(screen.queryAllByDisplayValue(/42/).length).toBe(1);
    expect(setValue).not.toHaveBeenCalled();
});

it('renders values less than the minimum as invalid', () => {
    render(<IntegerInput value="12" min="42" />)
    expect(screen.getByDisplayValue(/12/)).toBeInvalid()
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
