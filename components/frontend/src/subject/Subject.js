import React, { useEffect, useState } from 'react';
import { Dropdown, Table } from 'semantic-ui-react';
import { add_metric, copy_metric, move_metric } from '../api/metric';
import { get_subject_measurements } from '../api/subject';
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { TrendTable } from '../trendTable/TrendTable';
import { AddButton, CopyButton, MoveButton } from '../widgets/Button';
import { metric_options } from '../widgets/menu_options';
import { SubjectDetails } from './SubjectDetails';
import { SubjectTitle } from './SubjectTitle';


function displayedMetrics(allMetrics, hideMetricsNotRequiringAction, tags) {
  const metrics = {}
  Object.entries(allMetrics).forEach(([metric_uuid, metric]) => {
    if (hideMetricsNotRequiringAction && (metric.status === "target_met" || metric.status === "debt_target_met")) { return }
    if (tags.length > 0 && tags.filter(value => metric.tags.includes(value)).length === 0) { return }
    metrics[metric_uuid] = metric
  })
  return metrics
}


export function Subject(props) {

  const subject = props.report.subjects[props.subject_uuid];
  const metrics = displayedMetrics(subject.metrics, props.hideMetricsNotRequiringAction, props.tags)

  const [sortColumn, setSortColumn] = useState(null);
  const [view, setView] = useState('details');
  const [measurements, setMeasurements] = useState([]);

  useEffect(() => {
    get_subject_measurements(props.subject_uuid, props.report_date).then(json => {
      if (json.ok !== false) {
        setMeasurements(json.measurements)
      }
    })
  // eslint-disable-next-line
  }, []);

  const hamburgerItems = (
    <>
      <Dropdown.Header>Views</Dropdown.Header>
      <Dropdown.Item onClick={() => setView('details')}>
        Details
      </Dropdown.Item>
      <Dropdown.Item onClick={() => setView('measurements')}>
        Trend table
      </Dropdown.Item>
      <Dropdown.Header>Rows</Dropdown.Header>
      <Dropdown.Item onClick={() => props.setHideMetricsNotRequiringAction(!props.hideMetricsNotRequiringAction)}>
        {props.hideMetricsNotRequiringAction ? 'Show all metrics' : 'Hide metrics not requiring action'}
      </Dropdown.Item>
    </>
  )

  const subjectFooter = (
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
  return (
    <div id={props.subject_uuid}>
      <SubjectTitle subject={subject} {...props} />
      
        {view === 'details' ? 
        <Table sortable>
          <SubjectDetails 
            metrics={metrics} 
            setView={setView} 
            sortColumn={sortColumn} 
            setSortColumn={setSortColumn} 
            extraHamburgerItems={hamburgerItems}
            {...props}/>
          {subjectFooter}
        </Table>
          : <TrendTable
            datamodel={props.datamodel}
            reportDate={props.report_date}
            metrics={metrics}
            measurements={measurements}
            extraHamburgerItems={hamburgerItems}
            trendTableInterval={props.trendTableInterval}
            setTrendTableInterval={props.setTrendTableInterval}
            trendTableNrDates={props.trendTableNrDates}
            setTrendTableNrDates={props.setTrendTableNrDates}
            tableFooter={subjectFooter}
          />}
    </div>
  )
}
