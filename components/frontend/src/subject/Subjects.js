import React, { useState } from 'react';
import { Segment } from 'semantic-ui-react';
import { Subject } from './Subject';
import { add_subject } from '../api/subject';
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { AddButton } from '../widgets/Button';

export function Subjects(props) {
  const [hideMetricsNotRequiringAction, setHideMetricsNotRequiringAction] = useState(false);
  const last_index = Object.keys(props.report.subjects).length - 1;
  return (
    <>
      {Object.keys(props.report.subjects).map((subject_uuid, index) =>
        <Subject
          datamodel={props.datamodel}
          first_subject={index === 0}
          hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
          key={subject_uuid}
          last_subject={index === last_index}
          nr_new_measurements={props.nr_new_measurements}
          reload={props.reload}
          report={props.report}
          report_date={props.report_date}
          search_string={props.search_string}
          setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction}
          subject_uuid={subject_uuid}
          tags={props.tags}
          changed_fields={props.changed_fields}
        />
      )}
      <ReadOnlyOrEditable editableComponent={
        <Segment basic>
          <AddButton item_type={"subject"} onClick={() => add_subject(props.report.report_uuid, props.reload)} />
        </Segment>}
      />
    </>
  )
}
