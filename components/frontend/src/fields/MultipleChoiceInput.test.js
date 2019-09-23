import React from 'react';
import ReactDOM from 'react-dom';
import { MultipleChoiceInput } from './MultipleChoiceInput';

it('renders the value', () => {
  const div = document.createElement('div');
  ReactDOM.render(<MultipleChoiceInput value={["hello"]} options={["hello", "again"]} />, div);
  ReactDOM.unmountComponentAtNode(div);
});