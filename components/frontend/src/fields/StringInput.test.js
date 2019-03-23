import React from 'react';
import ReactDOM from 'react-dom';
import { StringInput } from './StringInput';

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<StringInput />, div);
  ReactDOM.unmountComponentAtNode(div);
});

it('renders the value', () => {
  const div = document.createElement('div');
  ReactDOM.render(<StringInput value="Hello" />, div);
  ReactDOM.unmountComponentAtNode(div);
});