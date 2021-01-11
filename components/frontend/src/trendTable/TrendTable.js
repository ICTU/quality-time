import React from 'react';
import { Table } from 'semantic-ui-react';
import { get_metric_name } from '../utils';
import { MeasurementsRow } from './MeasurementsRow';
import { TrendTableHeader } from './TrendTableHeader';


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


function sortAndOrganizeMeasurements(measurements) {
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


export function TrendTable({
    datamodel,
    reportDate,
    metrics,
    measurements,
    extraHamburgerItems,
    showTargets,
    trendTableInterval,
    setTrendTableInterval,
    trendTableNrDates,
    setTrendTableNrDates,
    tableFooter,
}) {

  const dates = columnDates(reportDate, trendTableInterval, trendTableNrDates)
  const orderedMeasurements = sortAndOrganizeMeasurements(measurements)
    
  return (
    <Table>
      <TrendTableHeader 
        extraHamburgerItems={extraHamburgerItems}
        columnDates={dates}
        trendTableInterval={trendTableInterval}
        setTrendTableInterval={setTrendTableInterval}
        trendTableNrDates={trendTableNrDates}
        setTrendTableNrDates={setTrendTableNrDates} />
      <Table.Body>
        {Object.entries(metrics).map(([metric_uuid, metric], index) => {
          const metricType = datamodel.metrics[metric.type]
          const metricName = get_metric_name(metric, datamodel)
          return (<MeasurementsRow key={index}
            metricType={metricType}
            metricName={metricName}
            metric={metric}
            dates={dates}
            metricMeasurements={orderedMeasurements[metric_uuid]}
            showTargetRow={showTargets}
            report_date={reportDate}
            trendTableInterval={trendTableInterval}
            trendTableNrDates={trendTableNrDates} />)
          })
        }
      </Table.Body>
      {tableFooter}
    </Table>
  )
}
