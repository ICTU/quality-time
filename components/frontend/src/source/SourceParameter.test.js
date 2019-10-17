import React from 'react';
import ReactDOM from 'react-dom';
import { SourceParameter } from './SourceParameter';

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<SourceParameter parameter_type="single_choice" parameter_values={["a"]} parameter_value="a" />, div);
  ReactDOM.unmountComponentAtNode(div);
});