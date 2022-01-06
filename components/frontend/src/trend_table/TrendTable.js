import React from 'react';
import { Table } from 'semantic-ui-react';
import { SubjectFooter } from '../subject/SubjectFooter';
import { MeasurementsRow } from './MeasurementsRow';
import { TrendTableHeader } from './TrendTableHeader';


function getColumnDates(report_date, trendTableInterval, trendTableNrDates) {
    const baseDate = report_date ? new Date(report_date) : new Date();
    const intervalLength = trendTableInterval;  // trendTableInterval is in days
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
    hiddenColumns,
    reportDate,
    metrics,
    measurements,
    extraHamburgerItems,
    trendTableInterval,
    setTrendTableInterval,
    trendTableNrDates,
    setTrendTableNrDates,
    subject_uuid,
    subject,
    report,
    reports,
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
                hiddenColumns={hiddenColumns}
                trendTableInterval={trendTableInterval}
                setTrendTableInterval={setTrendTableInterval}
                trendTableNrDates={trendTableNrDates}
                setTrendTableNrDates={setTrendTableNrDates} />
            <Table.Body>
                {Object.entries(metrics).map(([metric_uuid, metric], index) => {
                    return (
                        <MeasurementsRow key={metric_uuid}
                            changed_fields={changed_fields}
                            first_metric={index === 0}
                            last_metric={index === last_index}
                            metric_uuid={metric_uuid}
                            metric={metric}
                            dates={dates}
                            reportDate={reportDate}
                            report={report}
                            reports={reports}
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
                subjectUuid={subject_uuid}
                subject={subject}
                reload={reload}
                reports={reports}
                resetSortColumn={() => {/* Trend table is not sortable (yet) */ }} />
        </Table>
    )
}
