import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DatePicker } from './DatePicker';

it('calls the callback on date pick', async () => {
    let receivedValue;
    function mockCallback(_event, { value }) {
        receivedValue = value
    }
    render(<DatePicker onDate={mockCallback} value={new Date("2020-07-19")} />)
    await userEvent.type(screen.getByTestId("datepicker-input"), "20200720{Tab}", {initialSelectionStart: 0, initialSelectionEnd: 10})
    expect(receivedValue).toStrictEqual(new Date("2020-07-20T00:00:00"))
})

it('does not call the callback on an invalid date', async () => {
    let receivedValue;
    function mockCallback(_event, { value }) {
        receivedValue = value
    }
    render(<DatePicker onDate={mockCallback} value={new Date("2020-07-20")} />)
    await userEvent.type(screen.getByTestId("datepicker-input"), "20202121{Tab}", {initialSelectionStart: 0, initialSelectionEnd: 10})
    expect(receivedValue).toBe(null)
})

it('does not call the callback when the value is not a date', async () => {
    let receivedValue;
    function mockCallback(_event, { value }) {
        receivedValue = value
    }
    render(<DatePicker onDate={mockCallback} value={new Date("2020-07-20")} />)
    await userEvent.type(screen.getByTestId("datepicker-input"), "not a date{Tab}", {initialSelectionStart: 0, initialSelectionEnd: 10})
    expect(receivedValue).toBe(null)
})

it('calls the callback on clear', async () => {
    const mockCallback = jest.fn();
    const { container } = render(<DatePicker onDate={mockCallback} value={new Date("2020-07-20")} label="Report date" />)
    fireEvent.click(container.querySelector('.close'))
    expect(mockCallback).toHaveBeenCalledTimes(1)
})
