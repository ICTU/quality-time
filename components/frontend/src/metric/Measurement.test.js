import React from 'react';
import ReactDOM from 'react-dom';
import { Measurement } from './Measurement';

it('renders without crashing', () => {
  const container = document.createElement('tbody');
  ReactDOM.render(
    <Measurement
      measurements={[]}
      report={{
        report_uuid: "report_uuid",
        subjects: {
          subject_uuid: {
            metrics: {
              metric_uuid: {
                accept_debt: false,
                tags: [],
                type: "violations"
              }
            }
          }
        }
      }}
      metric_uuid="metric_uuid"
      subject_uuid="subject_uuid"
      datamodel={{ metrics: { violations: { direction: "≦", tags: [] } } }} />, container);
  ReactDOM.unmountComponentAtNode(container);
});
