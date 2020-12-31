import React, { useState } from 'react';
import { Table } from 'semantic-ui-react';
import { add_metric, copy_metric, move_metric } from '../api/metric';
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { AddButton, CopyButton, MoveButton } from '../widgets/Button';
import { metric_options } from '../widgets/menu_options';
import { SubjectDetails } from './SubjectDetails';
import { SubjectTitle } from './SubjectTitle';
import { SubjectTrendTable } from './SubjectTrendTable';

// ------------------------------- shared ----------------------------------------------
function displayedMetrics(allMetrics, hideMetricsNotRequiringAction, tags) {
  const metrics = {}
  Object.entries(allMetrics).forEach(([metric_uuid, metric]) => {
    if (hideMetricsNotRequiringAction && (metric.status === "target_met" || metric.status === "debt_target_met")) { return }
    if (tags.length > 0 && tags.filter(value => metric.tags.includes(value)).length === 0) { return }
    metrics[metric_uuid] = metric
  })
  return metrics
}

// --------------------------------- Component ------------------------------------------
export function Subject(props) {

  const subject = props.report.subjects[props.subject_uuid];
  const metrics = displayedMetrics(subject.metrics, props.hideMetricsNotRequiringAction, props.tags)

  const [sortColumn, setSortColumn] = useState(null);
  const [view, setView] = useState('details');

  function SubjectTableFooter() {
    return (
      <ReadOnlyOrEditable editableComponent={
        <Table.Footer>
          <Table.Row>
            <Table.HeaderCell colSpan='10'>
              <AddButton item_type="metric" onClick={() => {
                setSortColumn(null);
                add_metric(props.subject_uuid, props.reload);
              }}
              />
              <CopyButton
                item_type="metric"
                onChange={(source_metric_uuid) => {
                  setSortColumn(null);
                  copy_metric(source_metric_uuid, props.subject_uuid, props.reload);
                }}
                get_options={() => metric_options(props.reports, props.datamodel, subject.type)}
              />
              <MoveButton
                item_type="metric"
                onChange={(source_metric_uuid) => {
                  setSortColumn(null);
                  move_metric(source_metric_uuid, props.subject_uuid, props.reload);
                }}
                get_options={() => metric_options(props.reports, props.datamodel, subject.type, props.subject_uuid)}
              />
            </Table.HeaderCell>
          </Table.Row>
        </Table.Footer>}
      />
    )
  }
  return (
    <div id={props.subject_uuid}>
      <SubjectTitle subject={subject} {...props} />
      <Table sortable>
        {view === 'details' ? 
          <SubjectDetails 
            metrics={metrics} 
            setView={setView} 
            sortColumn={sortColumn} 
            setSortColumn={setSortColumn} 
            {...props}/>
          : <SubjectTrendTable 
            datamodel={props.datamodel} 
            subject_uuid={props.subject_uuid}
            report_date={props.report_date}
            metrics={metrics}
            setView={setView}
            trendTableInterval={props.trendTableInterval}
            setTrendTableInterval={props.setTrendTableInterval}
            trendTableNrDates={props.trendTableNrDates}
            setTrendTableNrDates={props.setTrendTableNrDates}
            hideMetricsNotRequiringAction={props.hideMetricsNotRequiringAction}
            setHideMetricsNotRequiringAction={props.setHideMetricsNotRequiringAction}
          />}
        <SubjectTableFooter />
      </Table>
    </div>
  )
}
