import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { TrendTable } from '../metric/TrendTable';

it('renders the trend starting from the current date', () => {
  render(
    <TrendTable
      measurements={[
        { count: { value: "33", target: "10", near_target: "20" }, start: "2019-09-25", end: "2019-09-30" },
        { count: { value: "34", target: "10", near_target: "20" }, start: "2019-09-10", end: "2019-09-25" },
      ]}
      metric={{ direction: "<", value: "42", target: "10", status: "target_met"}} report_date={null}
      trendTableInterval={1} trendTableNrDates={2} scale="count"
    />
  );
  expect(screen.getAllByText(/42/).length).toBe(1)
  expect(screen.getAllByText(/\?/).length).toBe(2)
  expect(screen.getAllByText(/\d\d\d\d/).length).toBe(2)
});

it('renders the trend starting from a fixed date', () => {
  render(
    <TrendTable
      measurements={[
        { count: { value: "33", target: "10", near_target: "20" }, start: "2019-09-25", end: "2019-09-30" },
        { count: { value: "34", target: "10", near_target: "20" }, start: "2019-09-10", end: "2019-09-25" },
      ]}
      metric={{ direction: "<" }} report_date={"2019-09-29"} trendTableInterval={1} trendTableNrDates={2}
      scale="count"
    />
  );
  expect(screen.getAllByText(/33/).length).toBe(1)
  expect(screen.getAllByText(/34/).length).toBe(1)
  expect(screen.getAllByText(/10/).length).toBe(2)
  expect(screen.getAllByText(/\d\d\d\d/).length).toBe(2)
});

it('renders the trend without data', () => {
  render(
    <TrendTable
      measurements={[]} metric={{ direction: "<", value: null, status: null, target: null}} report_date={null}
      trendTableInterval={1} trendTableNrDates={2} scale="count"
    />
  );
  expect(screen.getAllByText(/\?/).length).toBe(3)
  expect(screen.getAllByText(/\d\d\d\d/).length).toBe(2)
});

it('changes the number of columns', () => {
  const setTrendTableInterval = jest.fn();
  render(
    <TrendTable
      measurements={[]} metric={{ direction: "<", value: null, status: null, target: null}} report_date={null}
      trendTableInterval={1} trendTableNrDates={2} scale="count" setTrendTableInterval={setTrendTableInterval}
    />
  );
  fireEvent.click(screen.getByText(/2 weeks/));
  expect(setTrendTableInterval).toHaveBeenCalled()
});