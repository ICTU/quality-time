import React from 'react';
import ReactDOM from 'react-dom';
import Measurement from './Measurement';

it('renders without crashing', () => {
  const container = document.createElement('tbody');
  ReactDOM.render(
    <Measurement
      measurements={[]}
      metric={{accept_debt: false, type: "violations"}}
      datamodel={{metrics: {violations: {direction: "<="}}}} />, container);
  ReactDOM.unmountComponentAtNode(container);
});
