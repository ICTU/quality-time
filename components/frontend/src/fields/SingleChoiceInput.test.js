import React from 'react';
import ReactDOM from 'react-dom';
import { SingleChoiceInput } from './SingleChoiceInput';

it('renders the value', () => {
  const div = document.createElement('div');
  ReactDOM.render(<SingleChoiceInput value="hello" options={[{text: "Hello", value: "hello"}]} />, div);
  ReactDOM.unmountComponentAtNode(div);
});