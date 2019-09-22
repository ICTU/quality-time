import React from 'react';
import ReactDOM from 'react-dom';
import { DateInput } from './DateInput';

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<DateInput value="2019-09-30" />, div);
  ReactDOM.unmountComponentAtNode(div);
});

it('renders readonly without crashing ', () => {
  const div = document.createElement('div');
  ReactDOM.render(<DateInput value="2019-09-30" readOnly />, div);
  ReactDOM.unmountComponentAtNode(div);
});