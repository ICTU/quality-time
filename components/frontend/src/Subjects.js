import React from 'react';
import { Container } from 'semantic-ui-react';
import { Subject } from './Subject.js';


function Subjects(props) {
  return (
    <Container style={{ marginTop: '7em' }}>
      {Object.keys(props.subjects).map((subject_uuid) =>
        <Subject key={subject_uuid} subject_uuid={subject_uuid} subject={props.subjects[subject_uuid]}
          search_string={props.search_string} datamodel={props.datamodel} reload={props.reload}
          report_date={props.report_date} nr_new_measurements={props.nr_new_measurements} />)}
    </Container>
  )
}

export { Subjects };
