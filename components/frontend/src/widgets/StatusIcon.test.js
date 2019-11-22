import React from 'react';
import ReactDOM from 'react-dom';
import { StatusIcon } from './StatusIcon';

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<StatusIcon status="target_met" />, div);
  ReactDOM.unmountComponentAtNode(div);
});