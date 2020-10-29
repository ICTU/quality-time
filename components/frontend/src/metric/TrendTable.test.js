import React from 'react';
import { render, screen } from '@testing-library/react';
import { TrendTable } from './TrendTable';

it('renders 8 columns with dates', () => {
  render(<TrendTable measurements={[]} metric={{ direction: "<" }} report_date="2020-10-10" />);
  expect(screen.getAllByText(/\d\d\d\d/).length).toBe(8)
});

it('renders past measurements', () => {
  render(
    <TrendTable
      measurements={[{ count: { value: "42" }, start: "2019-09-29", end: "2019-10-01" }]}
      metric={{ direction: "<" }} report_date="2019-09-30" scale="count"
    />
  );
  expect(screen.getAllByText(/42/).length).toBe(1)
});

it('renders current measurement', () => {
  render(
    <TrendTable
      measurements={[{ count: { value: "1", target: "10", near_target: "20" }, start: "2019-09-29", end: "2019-09-30" }]}
      metric={{ direction: "<", value: 42 }} report_date={null} scale="count"
    />
  );
  expect(screen.getAllByText(/42/).length).toBe(1)
});