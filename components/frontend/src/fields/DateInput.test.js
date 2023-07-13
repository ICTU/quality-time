import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event';
import { Permissions } from '../context/Permissions';
import { DateInput } from './DateInput';

function renderDateInput(props) {
    return render(
        <Permissions.Provider value={false}>
            <DateInput {...props} />
        </Permissions.Provider>
    )
}

it('renders the value', () => {
    renderDateInput({ value: "2019-09-30" });
    expect(screen.getByDisplayValue("2019-09-30")).not.toBe(null);
})

it('renders the read only value', () => {
    renderDateInput({ value: "2019-09-30", requiredPermissions: ["test"] });
    expect(screen.getByDisplayValue("2019-09-30")).not.toBe(null);
})

it('clears the value', () => {
    let set_value = jest.fn()
    renderDateInput({ value: "2019-09-30", set_value: set_value, required: false });
    fireEvent.click(screen.getByRole("button"))
    expect(set_value).toHaveBeenCalledWith(null)
})

it('renders in error state if a value is missing and required', () => {
    renderDateInput({ value: "", required: true });
    expect(screen.getByDisplayValue("").parentElement.parentElement.parentElement.parentElement).toHaveClass("error");
})

it('submits the value when changed', async () => {
    let set_value = jest.fn()
    renderDateInput({ value: "2022-02-10", set_value: set_value })
    await userEvent.type(screen.getByDisplayValue("2022-02-10"), "2023-03-11{Tab}", {initialSelectionStart: 0, initialSelectionEnd: 10})
    expect(screen.getByDisplayValue("2023-03-11")).not.toBe(null)
    expect(set_value).toHaveBeenCalledWith("2023-03-11")
})

it('submits the value when the value is not changed', async () => {
    let set_value = jest.fn()
    const date = "2022-02-10"
    renderDateInput({ value: date, set_value: set_value })
    await userEvent.type(screen.getByDisplayValue(date), `${date}{Tab}`, {initialSelectionStart: 0, initialSelectionEnd: 10})
    expect(screen.getByDisplayValue(date)).not.toBe(null)
    expect(set_value).toHaveBeenCalledWith(date)
})

it('does not submit the value when the value is not valid', async () => {
    let set_value = jest.fn()
    const date = "2022-02-10"
    renderDateInput({ value: date, set_value: set_value })
    await userEvent.type(screen.getByDisplayValue(date), "invalid{Tab}", {initialSelectionStart: 0, initialSelectionEnd: 10})
    expect(set_value).not.toHaveBeenCalled()
})
