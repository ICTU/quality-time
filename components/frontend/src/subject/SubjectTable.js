import React, { useContext } from 'react';
import { Table } from '../semantic_ui_react_wrappers';
import { DataModel } from "../context/DataModel";
import { DarkMode } from "../context/DarkMode";
import { MetricDetails } from '../metric/MetricDetails';
import { IssueStatus } from '../measurement/IssueStatus';
import { MeasurementSources } from '../measurement/MeasurementSources';
import { MeasurementTarget } from '../measurement/MeasurementTarget';
import { MeasurementValue } from '../measurement/MeasurementValue';
import { TrendSparkline } from '../measurement/TrendSparkline';
import { StatusIcon } from '../measurement/StatusIcon';
import { TableRowWithDetails } from '../widgets/TableRowWithDetails';
import { Tag } from '../widgets/Tag';
import { formatMetricScale, get_metric_name, get_metric_tags, getMetricUnit } from '../utils';
import { SubjectTableFooter } from './SubjectTableFooter';
import { SubjectTableHeader } from './SubjectTableHeader';
import "./SubjectTable.css"

function MeasurementCells({ dates, metric, metric_uuid, measurements }) {
    return (
        <>
            {
                dates.map((date) => {
                    const iso_date_string = date.toISOString().split("T")[0];
                    const measurement = measurements?.find((m) => { return m.metric_uuid === metric_uuid && m.start.split("T")[0] <= iso_date_string && iso_date_string <= m.end.split("T")[0] })
                    let metric_value = measurement?.[metric.scale]?.value ?? "?";
                    const status = measurement?.[metric.scale]?.status ?? "unknown";
                    return (
                        <Table.Cell className={status} key={date} textAlign="right">{metric_value}{formatMetricScale(metric)}</Table.Cell>
                    )
                })
            }
        </>
    )
}

function expandVisibleDetailsTab(expand, metric_uuid, visibleDetailsTabs, toggleVisibleDetailsTab) {
    if (expand) {
        toggleVisibleDetailsTab(`${metric_uuid}:0`)
    } else {
        const tabs = visibleDetailsTabs.filter((each) => each?.startsWith(metric_uuid));
        if (tabs.length > 0) {
            toggleVisibleDetailsTab(tabs[0])
        }
    }
}

export function SubjectTable({
    changed_fields,
    dates,
    handleSort,
    hiddenColumns,
    measurements,
    metricEntries,
    reload,
    report,
    reportDate,
    reports,
    showIssueCreationDate,
    showIssueSummary,
    showIssueUpdateDate,
    sortDirection,
    sortColumn,
    subject,
    subject_uuid,
    toggleVisibleDetailsTab,
    visibleDetailsTabs
}) {
    const last_index = Object.entries(subject.metrics).length - 1;
    const className = "stickyHeader" + (subject.subtitle ? " subjectHasSubTitle" : "")
    const dataModel = useContext(DataModel)
    const darkMode = useContext(DarkMode)
    const nrDates = dates.length
    const style = nrDates > 1 ? { background: darkMode ? "rgba(60, 60, 60, 1)" : "#f9fafb" } : {}
    // Sort measurements in reverse order so that if there multiple measurements on a day, we find the most recent one:
    measurements.sort((m1, m2) => m1.start < m2.start ? 1 : -1)
    return (
        <Table sortable className={className} style={{ marginTop: "0px" }}>
            <SubjectTableHeader
                columnDates={dates}
                handleSort={handleSort}
                hiddenColumns={hiddenColumns}
                sortColumn={sortColumn}
                sortDirection={sortDirection}
            />
            <Table.Body>
                {metricEntries.map(([metric_uuid, metric], index) => {
                    const metricName = get_metric_name(metric, dataModel);
                    const unit = getMetricUnit(metric, dataModel)
                    return (
                        <TableRowWithDetails key={metric_uuid}
                            className={nrDates === 1 ? metric.status || "unknown" : ""}
                            details={
                                <MetricDetails
                                    first_metric={index === 0}
                                    last_metric={index === last_index}
                                    report_date={reportDate}
                                    reports={reports}
                                    report={report}
                                    subject_uuid={subject_uuid}
                                    metric_uuid={metric_uuid}
                                    changed_fields={changed_fields}
                                    visibleDetailsTabs={visibleDetailsTabs}
                                    toggleVisibleDetailsTab={toggleVisibleDetailsTab}
                                    stopSorting={() => handleSort(null)}
                                    reload={reload}
                                />
                            }
                            expanded={visibleDetailsTabs.filter((tab) => tab?.startsWith(metric_uuid)).length > 0}
                            id={metric_uuid}
                            onExpand={(expand) => expandVisibleDetailsTab(expand, metric_uuid, visibleDetailsTabs, toggleVisibleDetailsTab)}
                            style={style}
                        >
                            <Table.Cell style={style}>{metricName}</Table.Cell>
                            {nrDates > 1 && <MeasurementCells dates={dates} metric={metric} metric_uuid={metric_uuid} measurements={measurements} />}
                            {nrDates === 1 && !hiddenColumns.includes("trend") && <Table.Cell><TrendSparkline measurements={metric.recent_measurements} report_date={reportDate} scale={metric.scale} /></Table.Cell>}
                            {nrDates === 1 && !hiddenColumns.includes("status") && <Table.Cell textAlign='center'><StatusIcon status={metric.status} status_start={metric.status_start} /></Table.Cell>}
                            {nrDates === 1 && !hiddenColumns.includes("measurement") && <Table.Cell textAlign="right"><MeasurementValue metric={metric} /></Table.Cell>}
                            {nrDates === 1 && !hiddenColumns.includes("target") && <Table.Cell textAlign="right"><MeasurementTarget metric={metric} /></Table.Cell>}
                            {!hiddenColumns.includes("unit") && <Table.Cell style={style}>{unit}</Table.Cell>}
                            {!hiddenColumns.includes("source") && <Table.Cell style={style}><MeasurementSources metric={metric} /></Table.Cell>}
                            {!hiddenColumns.includes("comment") && <Table.Cell style={style}><div dangerouslySetInnerHTML={{ __html: metric.comment }} /></Table.Cell>}
                            {!hiddenColumns.includes("issues") && <Table.Cell style={style}>
                                <IssueStatus
                                    metric={metric}
                                    issueTrackerMissing={!report.issue_tracker && !report.report_uuid.startsWith("tag-")}
                                    showIssueCreationDate={showIssueCreationDate}
                                    showIssueSummary={showIssueSummary}
                                    showIssueUpdateDate={showIssueUpdateDate}
                                />
                            </Table.Cell>}
                            {!hiddenColumns.includes("tags") && <Table.Cell style={style}>{get_metric_tags(metric).map((tag) => <Tag key={tag} tag={tag} />)}</Table.Cell>}
                        </TableRowWithDetails>
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
