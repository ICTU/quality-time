import React from 'react';
import ReactDOM from 'react-dom';
import { TextInput } from './TextInput';

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<TextInput />, div);
  ReactDOM.unmountComponentAtNode(div);
});

it('renders the value', () => {
  const div = document.createElement('div');
  ReactDOM.render(<TextInput value="Hello" />, div);
  ReactDOM.unmountComponentAtNode(div);
});