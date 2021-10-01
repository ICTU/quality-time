import React from 'react';
import { Table } from 'semantic-ui-react';
import { SubjectFooter } from '../subject/SubjectFooter';
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
    changed_fields,
    datamodel,
    reportDate,
    metrics,
    measurements,
    extraHamburgerItems,
    trendTableInterval,
    setTrendTableInterval,
    trendTableNrDates,
    reports,
    setTrendTableNrDates,
    subject_uuid,
    subject,
    report,
    reports_overview,
    visibleDetailsTabs,
    toggleVisibleDetailsTab,
    reload
}) {

    const dates = getColumnDates(reportDate, trendTableInterval, trendTableNrDates)
    const last_index = Object.entries(subject.metrics).length - 1;

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
                    return (
                        <MeasurementsRow key={metric_uuid}
                            changed_fields={changed_fields}
                            datamodel={datamodel}
                            first_metric={index === 0}
                            last_metric={index === last_index}
                            metric_uuid={metric_uuid}
                            metricType={metricType}
                            metric={metric}
                            dates={dates}
                            reportDate={reportDate}
                            report={report}
                            reports_overview={reports_overview}
                            subject_uuid={subject_uuid}
                            measurements={measurements.filter((measurement) => measurement.metric_uuid === metric_uuid)}
                            visibleDetailsTabs={visibleDetailsTabs}
                            toggleVisibleDetailsTab={toggleVisibleDetailsTab}
                            reload={reload}
                        />
                    )
                })
                }
            </Table.Body>
            <SubjectFooter
                datamodel={datamodel}
                subjectUuid={subject_uuid}
                subject={subject}
                reload={reload}
                reports={reports}
                resetSortColumn={() => {/* Trend table is not sortable (yet) */ }} />
        </Table>
    )
}
