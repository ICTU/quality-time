import React from 'react';
import { Container, Dimmer, Loader } from 'semantic-ui-react';
import { Subject } from './Subject.js';


function Subjects(props) {
  if (props.subjects.length > 0) {
    return (
      <Container style={{ marginTop: '7em' }}>
        {props.subjects.map((subject, subject_index) =>
          <Subject key={subject.title} subject_index={subject_index} title={subject.title}
                   metrics={subject.metrics} search_string={props.search_string}
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
