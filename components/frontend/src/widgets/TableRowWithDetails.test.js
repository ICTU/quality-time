import React from 'react';
import ReactDOM from 'react-dom';
import { TableRowWithDetails } from './TableRowWithDetails';

it('renders without crashing', () => {
    const tbody = document.createElement('tbody');
    ReactDOM.render(<TableRowWithDetails />, tbody);
    ReactDOM.unmountComponentAtNode(tbody);
});