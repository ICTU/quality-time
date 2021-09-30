import React from 'react';
import ReactDOM from 'react-dom';
import { TrendGraph } from './TrendGraph';

it('renders without crashing', () => {
    const div = document.createElement('div');
    ReactDOM.render(<TrendGraph measurements={[]} />, div);
    ReactDOM.unmountComponentAtNode(div);
});

it('renders measurements without crashing', () => {
    const div = document.createElement('div');
    ReactDOM.render(<TrendGraph measurements={[{ count: { value: "1" }, start: "2019-09-29", end: "2019-09-30" }]} scale="count" />, div);
    ReactDOM.unmountComponentAtNode(div);
});

it('renders measurements with targets without crashing', () => {
    const div = document.createElement('div');
    ReactDOM.render(<TrendGraph measurements={[{ count: { value: "1", target: "10", near_target: "20" }, start: "2019-09-29", end: "2019-09-30" }]} scale="count" />, div);
    ReactDOM.unmountComponentAtNode(div);
});