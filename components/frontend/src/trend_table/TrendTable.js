import React from 'react';
import { Table } from 'semantic-ui-react';
import { get_metric_name } from '../utils';
import { MeasurementsRow } from './MeasurementsRow';
import { TrendTableHeader } from './TrendTableHeader';


function getColumnDates(report_date, trendTableInterval, trendTableNrDates) {
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


export function TrendTable({
  datamodel,
  reportDate,
  metrics,
  measurements,
  extraHamburgerItems,
  trendTableInterval,
  setTrendTableInterval,
  trendTableNrDates,
  setTrendTableNrDates,
  tableFooter,
}) {

  const dates = getColumnDates(reportDate, trendTableInterval, trendTableNrDates)

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
        {Object.entries(metrics).map(([metric_uuid, metric]) => {
          const metricType = datamodel.metrics[metric.type]
          const metricName = get_metric_name(metric, datamodel)
          return (
            <MeasurementsRow key={metric_uuid}
              metricType={metricType}
              metricName={metricName}
              metric={metric}
              dates={dates}
              measurements={measurements.filter((measurement) => measurement.metric_uuid === metric_uuid)}
            />
          )
        })
        }
      </Table.Body>
      {tableFooter}
    </Table>
  )
}
