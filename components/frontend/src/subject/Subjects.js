import React from 'react';
import { Button, Icon, Segment } from 'semantic-ui-react';
import { Subject } from './Subject';
import { add_subject } from '../api/subject';

export function Subjects(props) {
  return (
    <>
      {Object.keys(props.report.subjects).map((subject_uuid) =>
        <Subject
          datamodel={props.datamodel}
          key={subject_uuid}
          nr_new_measurements={props.nr_new_measurements}
          readOnly={props.readOnly}
          reload={props.reload}
          report={props.report}
          report_date={props.report_date}
          search_string={props.search_string}
          subject_uuid={subject_uuid}
          tags={props.tags}
          changed_filed={props.changed_filed}
        />
      )}
      {!props.readOnly &&
        <Segment basic>
          <Button icon primary basic onClick={() => add_subject(props.report.report_uuid, props.reload)}>
            <Icon name='plus' /> Add subject
            </Button>
        </Segment>}
    </>
  )
}
