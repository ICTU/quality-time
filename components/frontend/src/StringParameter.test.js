import React from 'react';
import ReactDOM from 'react-dom';
import { StringParameter } from './StringParameter.js';

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<StringParameter />, div);
  ReactDOM.unmountComponentAtNode(div);
});
