import React, { useEffect, useState } from 'react';
import { Dropdown, Table } from 'semantic-ui-react';
import { add_metric, copy_metric, move_metric } from '../api/metric';
import { get_subject_measurements } from '../api/subject';
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { Metric } from '../metric/Metric';
import { formatMetricScale, formatMetricUnit, get_metric_name, get_metric_target, get_source_name } from '../utils';
import { AddButton, CopyButton, MoveButton } from '../widgets/Button';
import { HamburgerMenu } from '../widgets/HamburgerMenu';
import { metric_options } from '../widgets/menu_options';
import { SubjectTitle } from './SubjectTitle';

// ------------------------------- for measurements view ------------------------------------
function sortedMetricMeasurements(measurements) {
  // sor measurements with descending start
  const sortedMeasurements = measurements.sort((m1, m2) => {
    return m1.start < m2.start
  })

  // put all measurements in a dictionary with metric as key
  const metricMeasurements = {}
  sortedMeasurements.forEach(measurement => {
    if (metricMeasurements[measurement.metric_uuid] === undefined) {
      metricMeasurements[measurement.metric_uuid] = [measurement]
    } else {
      metricMeasurements[measurement.metric_uuid].push(measurement)
    }
  })

  return metricMeasurements
}

function fetchSortedMeasurements(subject_uuid, report_date, setMeasurements) {
  get_subject_measurements(subject_uuid, report_date).then(json => {
    if (json.ok !== false) {
      const sortedMeasurements = sortedMetricMeasurements(json.measurements)
      setMeasurements(sortedMeasurements)
    }
  })
}

function columnDates(report_date, trendTableInterval, trendTableNrDates) {
  const baseDate = report_date ? new Date(report_date) : new Date();
  const intervalLength = trendTableInterval * 7;  // trendTableInterval is in weeks, convert to days
  const columnDates = []
  for (let offset = 0; offset < trendTableNrDates * intervalLength; offset += intervalLength) {
    let date = new Date(baseDate.getTime());
    date.setDate(date.getDate() - offset);
    columnDates.push(date)
  }
  return columnDates
}

function measurementCells(dates, measurements, metric) {
  return dates.map((columnDate, index) => {

    let measurement;
    if (index === 0) {
      measurement = measurements?.[0]
    } else {
      measurement = measurements?.find((measurement) => {
        return measurement.start <= columnDate.toISOString() && columnDate.toISOString() <= measurement.end
      })
    }
    
    const metric_value = !measurement?.count?.value ? "?" : measurement.count.value;
    const status = !measurement?.count?.status ? "unknown" : measurement.count.status;
    return <Table.Cell className={status} key={columnDate} textAlign="right">{metric_value}{formatMetricScale(metric)}</Table.Cell>
  })
}

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

// ------------------------------- for details view ------------------------------------
function createMetricComponents(props, metrics, setSortColumn) {
  const subject = props.report.subjects[props.subject_uuid];
  const last_index = Object.entries(subject.metrics).length - 1;

  let components = [];
  Object.entries(metrics).forEach(([metric_uuid, metric], index) => {
    components.push(
      <Metric
        first_metric={index === 0}
        hiddenColumns={props.hiddenColumns}
        key={metric_uuid}
        last_metric={index === last_index}
        metric_uuid={metric_uuid}
        metric={metric}
        stop_sort={() => setSortColumn(null)}
        {...props}
      />)
  });
  return components
}

function sortMetricComponents(datamodel, metricComponents, sortDirection, sortColumn) {
  const status_order = { "": "0", target_not_met: "1", debt_target_met: "2", near_target_met: "3", target_met: "4" };
  const sorters = {
    name: (m1, m2) => {
      const attribute1 = get_metric_name(m1.props.metric, datamodel);
      const attribute2 = get_metric_name(m2.props.metric, datamodel);
      return attribute1.localeCompare(attribute2)
    },
    measurement: (m1, m2) => {
      const attribute1 = m1.props.metric.value || "";
      const attribute2 = m2.props.metric.value || "";
      return attribute1.localeCompare(attribute2)
    },
    target: (m1, m2) => {
      const attribute1 = get_metric_target(m1.props.metric);
      const attribute2 = get_metric_target(m2.props.metric);
      return attribute1.localeCompare(attribute2)
    },
    comment: (m1, m2) => {
      const attribute1 = m1.props.metric.comment || '';
      const attribute2 = m2.props.metric.comment || '';
      return attribute1.localeCompare(attribute2)
    },
    status: (m1, m2) => {
      const attribute1 = status_order[m1.props.metric.status || ""];
      const attribute2 = status_order[m2.props.metric.status || ""];
      return attribute1.localeCompare(attribute2)
    },
    source: (m1, m2) => {
      let m1_sources = Object.values(m1.props.metric.sources).map((source) => get_source_name(source, datamodel));
      m1_sources.sort();
      let m2_sources = Object.values(m2.props.metric.sources).map((source) => get_source_name(source, datamodel));
      m2_sources.sort();
      const attribute1 = m1_sources.length > 0 ? m1_sources[0] : '';
      const attribute2 = m2_sources.length > 0 ? m2_sources[0] : '';
      return attribute1.localeCompare(attribute2)
    },
    tags: (m1, m2) => {
      let m1_tags = m1.props.metric.tags;
      m1_tags.sort();
      let m2_tags = m2.props.metric.tags;
      m2_tags.sort();
      const attribute1 = m1_tags.length > 0 ? m1_tags[0] : '';
      const attribute2 = m2_tags.length > 0 ? m2_tags[0] : '';
      return attribute1.localeCompare(attribute2)
    }
  }
  metricComponents.sort(sorters[sortColumn]);
  if (sortDirection === 'descending') {
    metricComponents.reverse()
  }
}

// --------------------------------- Component ------------------------------------------
export function Subject(props) {

  const subject = props.report.subjects[props.subject_uuid];
  const metrics = displayedMetrics(subject.metrics, props.hideMetricsNotRequiringAction, props.tags)

  const [sortColumn, setSortColumn] = useState(null);
  const [sortDirection, setSortDirection] = useState('ascending');
  const [view, setView] = useState('details');
  const [measurements, setMeasurements] = useState([]);

  useEffect(() => {
    if (view === 'measurements') {
      fetchSortedMeasurements(props.subject_uuid, props.report_date, setMeasurements);
    } 
    // eslint-disable-next-line
  }, [view]);
  // create_measurement_rows()

  let dates;
  let metricComponents = []
  let measurement_components = []
  if (view === 'details') {
    metricComponents = createMetricComponents(props, metrics, setSortColumn)
    if (sortColumn !== null) {
      sortMetricComponents(props.datamodel, metricComponents, sortDirection, sortColumn, setSortColumn)
    }
  }
  else if (view === 'measurements') {
    
    dates = columnDates(props.report_date, props.trendTableInterval, props.trendTableNrDates)

    Object.entries(metrics).forEach(([metricUuid, metric]) => {
      const metricMeasurements = measurements[metricUuid]
      const unit = formatMetricUnit(props.datamodel.metrics[metric.type], metric)
      measurement_components.push(
        <Table.Row key={metricUuid}>
          <Table.Cell></Table.Cell>
          <Table.Cell><strong>{get_metric_name(metric, props.datamodel)}</strong></Table.Cell>
          {measurementCells(dates, metricMeasurements, metric)}
          <Table.Cell><strong>{unit}</strong></Table.Cell>
        </Table.Row>)
    });
  }

  function handleSort(column) {
    if (sortColumn === column) {
      if (sortDirection === 'descending') {
        setSortColumn(null)  // Cycle through ascending->descending->no sort as long as the user clicks the same column
      }
      setSortDirection(sortDirection === 'ascending' ? 'descending' : 'ascending')
    } else {
      setSortColumn(column)
    }
  }
  
  function SortableHeader({ column, label, textAlign }) {
    const sorted = sortColumn === column ? sortDirection : null;
    return (
      <Table.HeaderCell onClick={() => handleSort(column)} sorted={sorted} textAlign={textAlign || 'left'}>
        {label}
      </Table.HeaderCell>
    )
  }
  
  function HamburgerHeader() {
    function ColumnMenuItem({ column }) {
      return (
        <Dropdown.Item onClick={() => props.toggleHiddenColumn(column)}>
          {props.hiddenColumns.includes(column) ? `Show ${column} column` : `Hide ${column} column`}
        </Dropdown.Item>
      )
    }
    return (
      <Table.HeaderCell collapsing textAlign="center">
        <HamburgerMenu>
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
          <Dropdown.Header>Columns</Dropdown.Header>
          <ColumnMenuItem column="trend" />
          <ColumnMenuItem column="status" />
          <ColumnMenuItem column="measurement" />
          <ColumnMenuItem column="target" />
          <ColumnMenuItem column="source" />
          <ColumnMenuItem column="comment" />
          <ColumnMenuItem column="tags" />
        </HamburgerMenu>
      </Table.HeaderCell>
    )
  }
  
  function TrendTableHamburger({setTrendTableNrDates, trendTableNrDates, setTrendTableInterval, trendTableInterval}) {
    return (
      <Table.HeaderCell collapsing textAlign="center">
        <HamburgerMenu>
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
          <Dropdown.Header>Number of dates</Dropdown.Header>
            {[2, 3, 4, 5, 6, 7].map((nr) =>
                <Dropdown.Item key={nr} active={nr === trendTableNrDates} onClick={() => setTrendTableNrDates(nr)}>{nr}</Dropdown.Item>
            )}
            <Dropdown.Header>Time between dates</Dropdown.Header>
            {[1, 2, 3, 4].map((nr) =>
                <Dropdown.Item key={nr} active={nr === trendTableInterval} onClick={() => setTrendTableInterval(nr)}>{`${nr} week${nr === 1 ? '' : 's'}`}</Dropdown.Item>
            )}
        </HamburgerMenu>
      </Table.HeaderCell>
    )
  }
  
  function SubjectTableHeader() {
    return (
      <Table.Header>
        <Table.Row>
          <HamburgerHeader />
          <SortableHeader column='name' label='Metric' />
          {!props.hiddenColumns.includes("trend") && <Table.HeaderCell width="2">Trend (7 days)</Table.HeaderCell>}
          {!props.hiddenColumns.includes("status") && <SortableHeader column='status' label='Status' textAlign='center' />}
          {!props.hiddenColumns.includes("measurement") && <SortableHeader column='measurement' label='Measurement' />}
          {!props.hiddenColumns.includes("target") && <SortableHeader column='target' label='Target' />}
          {!props.hiddenColumns.includes("source") && <SortableHeader column='source' label='Source' />}
          {!props.hiddenColumns.includes("comment") && <SortableHeader column='comment' label='Comment' />}
          {!props.hiddenColumns.includes("tags") && <SortableHeader column='tags' label='Tags' />}
        </Table.Row>
      </Table.Header>
    )
  }

  function TrendTableHeader({ dates, setTrendTableInterval, setTrendTableNrDates, trendTableInterval, trendTableNrDates }) {
    const cells = [];
    for (const date of dates) {
        cells.push(<Table.HeaderCell key={date} textAlign="right">{date.toLocaleDateString()}</Table.HeaderCell>);
    }
    return (
        <Table.Header>
            <Table.Row>
                <TrendTableHamburger 
                  setTrendTableInterval={setTrendTableInterval} 
                  setTrendTableNrDates={setTrendTableNrDates}
                  trendTableInterval={trendTableInterval} 
                  trendTableNrDates={trendTableNrDates} />
                <Table.HeaderCell>Metric</Table.HeaderCell>
                {cells}
                <Table.HeaderCell>Unit</Table.HeaderCell>
            </Table.Row>
        </Table.Header>
    )
}
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
        {view === 'details' ? <SubjectTableHeader /> : <TrendTableHeader dates={dates} setTrendTableInterval={props.setTrendTableInterval} setTrendTableNrDates={props.setTrendTableNrDates} trendTableInterval={props.trendTableInterval} trendTableNrDates={props.trendTableNrDates}/>}
        <Table.Body>{view === 'details' ? metricComponents : measurement_components}</Table.Body>
        <SubjectTableFooter />
      </Table>
    </div>
  )
}
