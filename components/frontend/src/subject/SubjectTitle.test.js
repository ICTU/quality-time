import React from 'react';
import ReactDOM from 'react-dom';
import { SubjectTitle } from './SubjectTitle';

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<SubjectTitle
    datamodel={{subjects: []}}
    report={{subjects: []}}
    subject={{type: "subject_type"}}
  />, div);
  ReactDOM.unmountComponentAtNode(div);
});