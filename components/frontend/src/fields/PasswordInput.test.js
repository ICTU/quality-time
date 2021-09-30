import React from 'react';
import ReactDOM from 'react-dom';
import { PasswordInput } from './PasswordInput';

it('renders without crashing', () => {
    const div = document.createElement('div');
    ReactDOM.render(<PasswordInput />, div);
    ReactDOM.unmountComponentAtNode(div);
});

it('renders the value', () => {
    const div = document.createElement('div');
    ReactDOM.render(<PasswordInput value="Hello" />, div);
    ReactDOM.unmountComponentAtNode(div);
});