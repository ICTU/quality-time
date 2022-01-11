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
    extraHamburgerItems,
    handleSort,
    hiddenColumns,
    measurements,
    metricEntries,
    reload,
    report,
    reports,
    reportDate,
    setTrendTableInterval,
    setTrendTableNrDates,
    sortDirection,
    sortColumn,
    subject,
    subject_uuid,
    toggleHiddenColumn,
    toggleVisibleDetailsTab,
    trendTableInterval,
    trendTableNrDates,
    visibleDetailsTabs
}) {

    const dates = getColumnDates(reportDate, trendTableInterval, trendTableNrDates)
    const last_index = Object.entries(subject.metrics).length - 1;

    return (
        <Table sortable>
            <TrendTableHeader
                columnDates={dates}
                extraHamburgerItems={extraHamburgerItems}
                handleSort={handleSort}
                hiddenColumns={hiddenColumns}
                setTrendTableInterval={setTrendTableInterval}
                setTrendTableNrDates={setTrendTableNrDates}
                sortColumn={sortColumn}
                sortDirection={sortDirection}
                toggleHiddenColumn={toggleHiddenColumn}
                trendTableNrDates={trendTableNrDates}
                trendTableInterval={trendTableInterval}
            />
            <Table.Body>
                {metricEntries.map(([metric_uuid, metric], index) => {
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
                            hiddenColumns={hiddenColumns}
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
