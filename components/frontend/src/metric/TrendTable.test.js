import React from 'react';
import ReactDOM from 'react-dom';
import { TrendTable } from './TrendTable';

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<TrendTable measurements={[]} report_date="2020-10-10" />, div);
  ReactDOM.unmountComponentAtNode(div);
});

it('renders measurements without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<TrendTable measurements={[{count: {value: "1"}, start: "2019-09-29", end: "2019-09-30"}]} report_date="2019-09-30" scale="count" />, div);
  ReactDOM.unmountComponentAtNode(div);
});

it('renders measurements with targets without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<TrendTable measurements={[{count: {value: "1", target: "10", near_target: "20"}, start: "2019-09-29", end: "2019-09-30"}]} report_date="2019-09-30" scale="count" />, div);
  ReactDOM.unmountComponentAtNode(div);
});