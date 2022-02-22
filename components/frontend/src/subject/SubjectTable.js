import React from 'react';
import { Table } from '../semantic_ui_react_wrappers/Table';
import { SubjectTableFooter } from './SubjectTableFooter';
import { SubjectTableRow } from './SubjectTableRow';
import { SubjectTableHeader } from './SubjectTableHeader';
import "./SubjectTable.css"

function getColumnDates(reportDate, dateInterval, dateOrder, nrDates) {
    const baseDate = reportDate ? new Date(reportDate) : new Date();
    const intervalLength = dateInterval;  // dateInterval is in days
    const columnDates = []
    for (let offset = 0; offset < nrDates * intervalLength; offset += intervalLength) {
        let date = new Date(baseDate.getTime());
        date.setDate(date.getDate() - offset);
        columnDates.push(date)
    }
    if (dateOrder === "ascending") { columnDates.reverse() }
    return columnDates
}

export function SubjectTable({
    changed_fields,
    dateInterval,
    dateOrder,
    handleSort,
    hiddenColumns,
    measurements,
    metricEntries,
    nrDates,
    reload,
    report,
    reportDate,
    reports,
    sortDirection,
    sortColumn,
    subject,
    subject_uuid,
    toggleVisibleDetailsTab,
    visibleDetailsTabs
}) {
    const dates = getColumnDates(reportDate, dateInterval, dateOrder, nrDates)
    const last_index = Object.entries(subject.metrics).length - 1;
    const className = "stickyHeader" + (subject.subtitle ? " subjectHasSubTitle" : "")
    return (
        <Table sortable className={className} style={{marginTop: "0px"}}>
            <SubjectTableHeader
                columnDates={dates}
                handleSort={handleSort}
                hiddenColumns={hiddenColumns}
                nrDates={nrDates}
                sortColumn={sortColumn}
                sortDirection={sortDirection}
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
