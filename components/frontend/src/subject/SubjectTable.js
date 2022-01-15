import React from 'react';
import { Table } from 'semantic-ui-react';
import { SubjectTableFooter } from './SubjectTableFooter';
import { SubjectTableRow } from './SubjectTableRow';
import { SubjectTableHeader } from './SubjectTableHeader';


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


export function SubjectTable({
    changed_fields,
    clearVisibleDetailsTabs,
    handleSort,
    hiddenColumns,
    hideMetricsNotRequiringAction,
    measurements,
    metricEntries,
    reload,
    report,
    reports,
    reportDate,
    setHideMetricsNotRequiringAction,
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
            <SubjectTableHeader
                clearVisibleDetailsTabs={clearVisibleDetailsTabs}
                columnDates={dates}
                handleSort={handleSort}
                hiddenColumns={hiddenColumns}
                hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
                setHideMetricsNotRequiringAction={setHideMetricsNotRequiringAction}
                setTrendTableInterval={setTrendTableInterval}
                setTrendTableNrDates={setTrendTableNrDates}
                sortColumn={sortColumn}
                sortDirection={sortDirection}
                toggleHiddenColumn={toggleHiddenColumn}
                trendTableNrDates={trendTableNrDates}
                trendTableInterval={trendTableInterval}
                visibleDetailsTabs={visibleDetailsTabs}
            />
            <Table.Body>
                {metricEntries.map(([metric_uuid, metric], index) => {
                    return (
                        <SubjectTableRow key={metric_uuid}
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
                            trendTableNrDates={trendTableNrDates}
                            reload={reload}
                        />
                    )
                })
                }
            </Table.Body>
            <SubjectTableFooter
                subjectUuid={subject_uuid}
                subject={subject}
                reload={reload}
                reports={reports}
                resetSortColumn={() => handleSort(null)} />
        </Table>
    )
}
