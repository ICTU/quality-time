import React from 'react';
import ReactDOM from 'react-dom';
import { StringParameter } from './StringParameter.js';

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<StringParameter />, div);
  ReactDOM.unmountComponentAtNode(div);
});

it('renders the parameter value', () => {
  const div = document.createElement('div');
  const sp = ReactDOM.render(<StringParameter paramter_value="Hello" />, div);
  ReactDOM.unmountComponentAtNode(div);
});