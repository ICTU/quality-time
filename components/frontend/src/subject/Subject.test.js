import React from 'react';
import ReactDOM from 'react-dom';
import { Subject } from './Subject';

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<Subject
    datamodel={{subjects: []}}
    report={{subjects: {subject_uuid: {metrics: []}}}}
    subject_uuid="subject_uuid"
    subject={{type: "subject_type"}}
  />, div);
  ReactDOM.unmountComponentAtNode(div);
});