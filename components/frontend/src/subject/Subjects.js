import React from 'react';
import { Segment } from 'semantic-ui-react';
import { Subject } from './Subject';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { CopyButton, AddButton, MoveButton } from '../widgets/Button';
import { add_subject, copy_subject, move_subject } from '../api/subject';
import { subject_options } from '../widgets/menu_options';
import { useDelayedRender, useURLSearchQuery } from '../utils';

export function Subjects(props) {
  const visible = useDelayedRender();
  const [hideMetricsNotRequiringAction, setHideMetricsNotRequiringAction] = useURLSearchQuery(props.history, "hide_metrics_not_requiring_action", "boolean");
  const [visibleDetailsTabs, toggleVisibleDetailsTab, clearVisibleDetailsTabs] = useURLSearchQuery(props.history, "tabs", "array");
  const [subjectTrendTable, setSubjectTrendTable] = useURLSearchQuery(props.history, "subject_trend_table", "boolean")
  const [trendTableNrDates, setTrendTableNrDates] = useURLSearchQuery(props.history, "trend_table_nr_dates", "integer", 7);
  const [trendTableInterval, setTrendTableInterval] = useURLSearchQuery(props.history, "trend_table_interval", "integer", 1);
  const last_index = Object.keys(props.report.subjects).length - 1;
  return (
    <>
      {Object.keys(props.report.subjects).map((subject_uuid, index) =>
        visible || index < 3 ?
          <Subject
            {...props}
            clearHiddenColumns={props.clearHiddenColumns}
            clearVisibleDetailsTabs={clearVisibleDetailsTabs}
            first_subject={index === 0}
            hiddenColumns={props.hiddenColumns}
            hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
            key={subject_uuid}
            last_subject={index === last_index}
            setHideMetricsNotRequiringAction={(state) => setHideMetricsNotRequiringAction(state)}
            setSubjectTrendTable={(state) => setSubjectTrendTable(state)}
            setTrendTableNrDates={(nr) => setTrendTableNrDates(nr)}
            setTrendTableInterval={(interval) => setTrendTableInterval(interval)}
            subjectTrendTable={subjectTrendTable}
            subject_uuid={subject_uuid}
            toggleHiddenColumn={props.toggleHiddenColumn}
            toggleVisibleDetailsTab={(...tabs) => toggleVisibleDetailsTab(...tabs)}
            trendTableInterval={trendTableInterval}
            trendTableNrDates={trendTableNrDates}
            visibleDetailsTabs={visibleDetailsTabs}
          /> : null
      )}
      <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
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
