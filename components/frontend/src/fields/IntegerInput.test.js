import React from 'react';
import ReactDOM from 'react-dom';
import { IntegerInput } from './IntegerInput';

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<IntegerInput />, div);
  ReactDOM.unmountComponentAtNode(div);
});

it('renders the value', () => {
  const div = document.createElement('div');
  ReactDOM.render(<IntegerInput value="42" />, div);
  ReactDOM.unmountComponentAtNode(div);
});
