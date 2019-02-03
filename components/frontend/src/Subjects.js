import React from 'react';
import { Container, Dimmer, Loader } from 'semantic-ui-react';
import { Subject } from './Subject.js';


function Subjects(props) {
  if (Object.keys(props.subjects).length > 0) {
    return (
      <Container style={{ marginTop: '7em' }}>
        {Object.keys(props.subjects).map((subject_uuid) =>
          <Subject key={subject_uuid} subject_uuid={subject_uuid} subject={props.subjects[subject_uuid]}
            search_string={props.search_string} datamodel={props.datamodel} reload={props.reload}
            report_date={props.report_date} nr_new_measurements={props.nr_new_measurements} />)}
      </Container>
    )
  }
  return (
    <Container style={{ marginTop: '7em' }}>
      <Dimmer active inverted>
        <Loader size='large'>Loading</Loader>
      </Dimmer>
    </Container>
  )
}

export { Subjects };
