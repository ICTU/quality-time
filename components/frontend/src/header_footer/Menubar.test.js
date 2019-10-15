import React from 'react';
import ReactDOM from 'react-dom';
import { Menubar } from './Menubar';

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<Menubar report_date_string="2019-10-10" onDate={console.log} />, div);
  ReactDOM.unmountComponentAtNode(div);
});