import React from 'react';
import ReactDOM from 'react-dom';
import { TrendSparkline } from './TrendSparkline';

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<TrendSparkline measurements={[]} />, div);
  ReactDOM.unmountComponentAtNode(div);
});

it('renders measurements without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<TrendSparkline measurements={[{value: "1", start: "2019-09-29", end: "2019-09-30"}]} />, div);
  ReactDOM.unmountComponentAtNode(div);
});