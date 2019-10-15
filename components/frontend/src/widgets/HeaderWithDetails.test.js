import React from 'react';
import ReactDOM from 'react-dom';
import { HeaderWithDetails } from './HeaderWithDetails';

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<HeaderWithDetails />, div);
  ReactDOM.unmountComponentAtNode(div);
});