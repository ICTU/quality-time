import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react'
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
    const { container } = renderDateInput({ value: "2019-09-30", set_value: set_value });
    fireEvent.click(container.querySelector(".remove"))
    expect(screen.queryByDisplayValue("2019-09-30")).toBe(null);
})

it('renders in error state if a value is missing and required', () => {
    renderDateInput({ value: "", required: true });
    expect(screen.getByDisplayValue("")).toBeInvalid();
})

it('submits the value when changed', async () => {
    let set_value = jest.fn()
    renderDateInput({ value: "2022-02-10", set_value: set_value })
    await act(async () => fireEvent.change(screen.getByDisplayValue("2022-02-10"), {target: {value: '2023-03-11'}}))
    expect(screen.getByDisplayValue("2023-03-11")).not.toBe(null)
    expect(set_value).toHaveBeenCalledWith("2023-03-11")
})

it('does not submit the value when the value is not changed', async () => {
    let set_value = jest.fn()
    const date = "2022-02-10"
    renderDateInput({ value: date, set_value: set_value })
    await act(async () => fireEvent.change(screen.getByDisplayValue(date), {target: {value: date}}))
    expect(screen.getByDisplayValue(date)).not.toBe(null)
    expect(set_value).not.toHaveBeenCalled()
})

it('does not submit the value when the value is not valid', async () => {
    let set_value = jest.fn()
    const date = "2022-02-10"
    renderDateInput({ value: date, set_value: set_value })
    await act(async () => fireEvent.change(screen.getByDisplayValue(date), {target: {value: "invalid"}}))
    expect(screen.getByDisplayValue("invalid")).not.toBe(null)
    expect(set_value).not.toHaveBeenCalled()
})
