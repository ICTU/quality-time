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
    ReactDOM.render(<TrendSparkline measurements={[{ count: { value: "1" }, start: "2019-09-29", end: "2019-09-30" }]} scale="count" />, div);
    ReactDOM.unmountComponentAtNode(div);
});

it('renders old measurements without crashing', () => {
    const div = document.createElement('div');
    const now = new Date("2020-01-01");
    ReactDOM.render(<TrendSparkline measurements={[{ count: { value: "1" }, start: "2019-09-29", end: "2019-09-30" }]} report_date={now} scale="count" />, div);
    ReactDOM.unmountComponentAtNode(div);
});