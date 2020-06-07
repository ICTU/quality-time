import React, { useEffect, useState } from 'react';
import { Segment } from 'semantic-ui-react';
import { Subject } from './Subject';
import { add_subject, copy_subject } from '../api/subject';
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { AddOrCopyButton } from '../widgets/Button';
import { subject_options } from '../menu_options';

function useDelayedRender() {
  const [visible, setVisible] = useState(false);
  useEffect(() => { setTimeout(setVisible, 50, true) }, []);
  return visible;
}

export function Subjects(props) {
  const visible = useDelayedRender();
  const [hideMetricsNotRequiringAction, setHideMetricsNotRequiringAction] = useState(false);
  const last_index = Object.keys(props.report.subjects).length - 1;
  return (
    <>
      {Object.keys(props.report.subjects).map((subject_uuid, index) =>
        visible || index < 3 ?
        <Subject
          {...props}
          first_subject={index === 0}
          hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
          key={subject_uuid}
          last_subject={index === last_index}
          setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction}
          subject_uuid={subject_uuid}
        /> : null
      )}
      <ReadOnlyOrEditable editableComponent={
        <Segment basic>
          <AddOrCopyButton
            item_type={"subject"}
            onChange={
              (source_subject_uuid) => copy_subject(source_subject_uuid, props.report.report_uuid, props.reload)}
            onClick={() => add_subject(props.report.report_uuid, props.reload)}
            options={subject_options(props.reports, props.datamodel)}
          />
        </Segment>}
      />
    </>
  )
}
