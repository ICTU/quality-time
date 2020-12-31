import React, { useEffect, useState } from 'react';
import { Dropdown, Table } from 'semantic-ui-react';
import { get_subject_measurements } from '../api/subject';
import { formatMetricScale, formatMetricUnit, get_metric_name } from '../utils';
import { HamburgerMenu } from '../widgets/HamburgerMenu';

// ------------------------------- for measurements view ------------------------------------
function sortedMetricMeasurements(measurements) {
  // sort measurements with descending start
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

    const metric_value = !measurement?.[metric.scale]?.value ? "?" : measurement[metric.scale].value;
    const status = !measurement?.[metric.scale]?.status ? "unknown" : measurement.[metric.scale].status;
    return <Table.Cell className={status} key={columnDate} textAlign="right">{metric_value}{formatMetricScale(metric)}</Table.Cell>
  })
}

export function SubjectTrendTable({
    datamodel,
    subject_uuid,
    report_date,
    metrics,
    setView,
    trendTableInterval,
    setTrendTableInterval,
    trendTableNrDates,
    setTrendTableNrDates,
    hideMetricsNotRequiringAction,
    setHideMetricsNotRequiringAction,
}) {
  const [measurements, setMeasurements] = useState([]);

  useEffect(() => {
    get_subject_measurements(subject_uuid, report_date).then(json => {
      if (json.ok !== false) {
        const sortedMeasurements = sortedMetricMeasurements(json.measurements)
        setMeasurements(sortedMeasurements)
      }
    })
  // eslint-disable-next-line
  }, []);

  const dates = columnDates(report_date, trendTableInterval, trendTableNrDates)
  let measurementComponents = []
  Object.entries(metrics).forEach(([metricUuid, metric]) => {
    const metricMeasurements = measurements[metricUuid]
    const unit = formatMetricUnit(datamodel.metrics[metric.type], metric)
    measurementComponents.push(
      <Table.Row key={metricUuid}>
        <Table.Cell></Table.Cell>
        <Table.Cell><strong>{get_metric_name(metric, datamodel)}</strong></Table.Cell>
        {measurementCells(dates, metricMeasurements, metric)}
        <Table.Cell><strong>{unit}</strong></Table.Cell>
      </Table.Row>)});
  
  function HamburgerHeader() {
    return (
      <Table.HeaderCell collapsing textAlign="center">
        <HamburgerMenu onClick={() => {console.log("clicl")}}>
          <Dropdown.Header>Views</Dropdown.Header>
          <Dropdown.Item onClick={() => setView('details')}>
            Details
          </Dropdown.Item>
          <Dropdown.Item onClick={() => setView('measurements')}>
            Trend table
          </Dropdown.Item>
          <Dropdown.Header>Rows</Dropdown.Header>
          <Dropdown.Item onClick={() => setHideMetricsNotRequiringAction(!hideMetricsNotRequiringAction)}>
            {hideMetricsNotRequiringAction ? 'Show all metrics' : 'Hide metrics not requiring action'}
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


  function TrendTableHeader() {
    const cells = [];
    for (const date of dates) {
        cells.push(<Table.HeaderCell key={date} textAlign="right">{date.toLocaleDateString()}</Table.HeaderCell>);
    }
    return (
        <Table.Header>
            <Table.Row>
                <HamburgerHeader />
                <Table.HeaderCell>Metric</Table.HeaderCell>
                {cells}
                <Table.HeaderCell>Unit</Table.HeaderCell>
            </Table.Row>
        </Table.Header>
    )
}
  return (
    <>
      <TrendTableHeader />
      <Table.Body>{measurementComponents}</Table.Body>
    </>
  )
}
