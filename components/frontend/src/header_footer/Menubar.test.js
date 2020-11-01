import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { Menubar } from './Menubar';

it('scrolls to the dashboard', async () => {
  const scrollIntoView = jest.fn();
  scrollIntoView.mockImplementation(() => { return { scrollIntoView: jest.fn() } });
  Object.defineProperty(global.document, 'getElementById', { value: scrollIntoView });
  Object.defineProperty(global.window, 'scrollBy', { value: jest.fn() });
  await act(async () => {
    render(<Menubar report_date_string="2019-10-10" onDate={console.log} />);
    fireEvent.click(screen.getByLabelText(/Scroll to dashboard/));
  });
  expect(scrollIntoView).toHaveBeenCalled()
});

it('does not crash if there is no dashboard', async () => {
  const scrollIntoView = jest.fn();
  scrollIntoView.mockImplementation(() => { return { scrollIntoView: jest.fn() } });
  Object.defineProperty(global.document, 'getElementById', {});
  Object.defineProperty(global.window, 'scrollBy', { value: jest.fn() });
  await act(async () => {
    render(<Menubar report_date_string="2019-10-10" onDate={console.log} />);
    fireEvent.click(screen.getByLabelText(/Scroll to dashboard/));
  });
  expect(scrollIntoView).not.toHaveBeenCalled()
});