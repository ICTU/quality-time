import React from 'react';
import { Segment } from 'semantic-ui-react';
import { Subject } from './Subject';
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { CopyButton, AddButton, MoveButton } from '../widgets/Button';
import { add_subject, copy_subject, move_subject } from '../api/subject';
import { subject_options } from '../widgets/menu_options';
import { useDelayedRender, useURLSearchQuery } from '../utils';

export function Subjects(props) {
  const visible = useDelayedRender();
  const [hideMetricsNotRequiringAction, setHideMetricsNotRequiringAction] = useURLSearchQuery(props.history, "hide_metrics_not_requiring_action", "boolean");
  const [hiddenColumns, toggleHiddenColumn, clearHiddenColumns] = useURLSearchQuery(props.history, "hidden_columns", "array");
  const [visibleColumns, toggleVisibleColumn, clearVisibleColumns] = useURLSearchQuery(props.history, "visible_columns", "array");
  const [visibleDetailsTabs, toggleVisibleDetailsTab, clearVisibleDetailsTabs] = useURLSearchQuery(props.history, "tabs", "array");
  const last_index = Object.keys(props.report.subjects).length - 1;
  return (
    <>
      {Object.keys(props.report.subjects).map((subject_uuid, index) =>
        visible || index < 3 ?
          <Subject
            {...props}
            clearHiddenColumns={clearHiddenColumns}
            clearVisibleColumns={clearVisibleColumns}
            clearVisibleDetailsTabs={clearVisibleDetailsTabs}
            first_subject={index === 0}
            hiddenColumns={hiddenColumns}
            hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
            key={subject_uuid}
            last_subject={index === last_index}
            setHideMetricsNotRequiringAction={(state) => setHideMetricsNotRequiringAction(state)}
            setVisibleColumns={(columns) => setVisibleColumns(columns)}
            subject_uuid={subject_uuid}
            toggleHiddenColumn={(column) => toggleHiddenColumn(column)}
            toggleVisibleColumn={(column) => toggleVisibleColumn(column)}
            toggleVisibleDetailsTab={(...tabs) => toggleVisibleDetailsTab(...tabs)}
            visibleDetailsTabs={visibleDetailsTabs}
            visibleColumns={visibleColumns}
          /> : null
      )}
      <ReadOnlyOrEditable editableComponent={
        <Segment basic>
          <AddButton item_type="subject" onClick={() => add_subject(props.report.report_uuid, props.reload)} />
          <CopyButton
            item_type="subject"
            onChange={(source_subject_uuid) => copy_subject(source_subject_uuid, props.report.report_uuid, props.reload)}
            get_options={() => subject_options(props.reports, props.datamodel)}
          />
          <MoveButton
            item_type="subject"
            onChange={(source_subject_uuid) => move_subject(source_subject_uuid, props.report.report_uuid, props.reload)}
            get_options={() => subject_options(props.reports, props.datamodel, props.report.report_uuid)}
          />
        </Segment>}
      />
    </>
  )
}
