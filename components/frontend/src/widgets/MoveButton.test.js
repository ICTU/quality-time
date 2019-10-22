import React from 'react';
import ReactDOM from 'react-dom';
import { MoveButtonGroup } from './MoveButton';

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<MoveButtonGroup />, div);
  ReactDOM.unmountComponentAtNode(div);
});