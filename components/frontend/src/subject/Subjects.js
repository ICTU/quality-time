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
          {...props}
          first_subject={index === 0}
          hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
          key={subject_uuid}
          last_subject={index === last_index}
          setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction}
          subject_uuid={subject_uuid}
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
