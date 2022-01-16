import React from 'react';
import { Table } from 'semantic-ui-react';
import { SubjectTableFooter } from './SubjectTableFooter';
import { SubjectTableRow } from './SubjectTableRow';
import { SubjectTableHeader } from './SubjectTableHeader';


function getColumnDates(reportDate, dateInterval, nrDates) {
    const baseDate = reportDate ? new Date(reportDate) : new Date();
    const intervalLength = dateInterval;  // dateInterval is in days
    const columnDates = []
    for (let offset = 0; offset < nrDates * intervalLength; offset += intervalLength) {
        let date = new Date(baseDate.getTime());
        date.setDate(date.getDate() - offset);
        columnDates.push(date)
    }
    return columnDates
}


export function SubjectTable({
    changed_fields,
    clearVisibleDetailsTabs,
    dateInterval,
    handleSort,
    hiddenColumns,
    hideMetricsNotRequiringAction,
    measurements,
    metricEntries,
    nrDates,
    reload,
    report,
    reports,
    reportDate,
    setDateInterval,
    setHideMetricsNotRequiringAction,
    setNrDates,
    sortDirection,
    sortColumn,
    subject,
    subject_uuid,
    toggleHiddenColumn,
    toggleVisibleDetailsTab,
    visibleDetailsTabs
}) {

    const dates = getColumnDates(reportDate, dateInterval, nrDates)
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
                setDateInterval={setDateInterval}
                setNrDates={setNrDates}
                sortColumn={sortColumn}
                sortDirection={sortDirection}
                toggleHiddenColumn={toggleHiddenColumn}
                nrDates={nrDates}
                dateInterval={dateInterval}
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
                            nrDates={nrDates}
                            reload={reload}
                            stopSorting={() => handleSort(null)}
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
                stopSorting={() => handleSort(null)} />
        </Table>
    )
}
