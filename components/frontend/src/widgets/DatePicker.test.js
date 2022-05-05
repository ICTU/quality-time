import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DatePicker } from './DatePicker';

it('calls the callback on date pick', async () => {
    const mockCallback = jest.fn();
    render(<DatePicker onDate={mockCallback} name="report_date_string" value="20-07-2020" label="Report date" />)
    await userEvent.type(screen.getByLabelText("Report date"), "21-07-2020", {initialSelectionStart: 0, initialSelectionEnd: 10})
    expect(mockCallback).toHaveBeenCalledTimes(1);
})

it('does not call the callback on an invalid date', async () => {
    const mockCallback = jest.fn();
    render(<DatePicker onDate={mockCallback} name="report_date_string" value="20-07-2020" label="Report date" />)
    await userEvent.type(screen.getByLabelText("Report date"), "21-21-2020", {initialSelectionStart: 0, initialSelectionEnd: 10})
    expect(mockCallback).not.toHaveBeenCalled()
})

it('does not call the callback when the value is not a date', async () => {
    const mockCallback = jest.fn();
    render(<DatePicker onDate={mockCallback} name="report_date_string" value="20-07-2020" label="Report date" />)
    await userEvent.type(screen.getByLabelText("Report date"), "not a date", {initialSelectionStart: 0, initialSelectionEnd: 10})
    expect(mockCallback).not.toHaveBeenCalled()
})

it('calls the callback on clear', async () => {
    const mockCallback = jest.fn();
    const { container } = render(<DatePicker onDate={mockCallback} name="report_date_string" value="20-07-2020" label="Report date" />)
    fireEvent.click(container.querySelector('.remove'))
    expect(mockCallback).toHaveBeenCalledTimes(1)
})
