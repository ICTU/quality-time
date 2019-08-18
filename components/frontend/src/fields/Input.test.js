import React from 'react';
import ReactDOM from 'react-dom';
import { Input } from './Input';

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<Input />, div);
  ReactDOM.unmountComponentAtNode(div);
});

it('renders the value', () => {
  const div = document.createElement('div');
  ReactDOM.render(<Input value="Hello" />, div);
  ReactDOM.unmountComponentAtNode(div);
});