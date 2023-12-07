import React, { useContext } from 'react';
import PropTypes from 'prop-types';
import { Table } from '../semantic_ui_react_wrappers';
import { DataModel } from "../context/DataModel";
import { DarkMode } from "../context/DarkMode";
import { IssueStatus } from '../issue/IssueStatus';
import { MetricDetails } from '../metric/MetricDetails';
import { MeasurementSources } from '../measurement/MeasurementSources';
import { MeasurementTarget } from '../measurement/MeasurementTarget';
import { MeasurementValue } from '../measurement/MeasurementValue';
import { StatusIcon } from '../measurement/StatusIcon';
import { Overrun } from '../measurement/Overrun';
import { TimeLeft } from '../measurement/TimeLeft';
import { TrendSparkline } from '../measurement/TrendSparkline';
import { TableRowWithDetails } from '../widgets/TableRowWithDetails';
import { Tag } from '../widgets/Tag';
import { formatMetricScale, get_metric_name, getMetricTags, getMetricUnit } from '../utils';
import { SubjectTableFooter } from './SubjectTableFooter';
import { SubjectTableHeader } from './SubjectTableHeader';
import "./SubjectTable.css"
import {
    datesPropType,
    optionalDatePropType,
    reportPropType,
    reportsPropType,
    settingsPropType,
    stringsPropType,
} from '../sharedPropTypes';

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

function expandVisibleDetailsTab(expand, metric_uuid, visibleDetailsTabs) {
    if (expand) {
        visibleDetailsTabs.toggle(`${metric_uuid}:0`)
    } else {
        const tabs = visibleDetailsTabs.value.filter((each) => each?.startsWith(metric_uuid));
        if (tabs.length > 0) {
            visibleDetailsTabs.toggle(tabs[0])
        }
    }
}

export function SubjectTable({
    changed_fields,
    dates,
    handleSort,
    measurements,
    metricEntries,
    reload,
    report,
    reportDate,
    reports,
    settings,
    subject,
    subject_uuid
}) {
    const last_index = Object.entries(subject.metrics).length - 1;
    const className = "stickyHeader" + (subject.subtitle ? " subjectHasSubTitle" : "")
    const dataModel = useContext(DataModel)
    const darkMode = useContext(DarkMode)
    const nrDates = dates.length
    const style = nrDates > 1 ? { background: darkMode ? "rgba(60, 60, 60, 1)" : "#f9fafb" } : {}
    // Sort measurements in reverse order so that if there multiple measurements on a day, we find the most recent one:
    const reversedMeasurements = measurements.slice().sort((m1, m2) => m1.start < m2.start ? 1 : -1)
    return (
        <Table sortable className={className} style={{ marginTop: "0px" }}>
            <SubjectTableHeader
                columnDates={dates}
                handleSort={handleSort}
                settings={settings}
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
                                    changed_fields={changed_fields}
                                    first_metric={index === 0}
                                    last_metric={index === last_index}
                                    metric_uuid={metric_uuid}
                                    reload={reload}
                                    report_date={reportDate}
                                    reports={reports}
                                    report={report}
                                    stopFilteringAndSorting={() => {
                                        handleSort(null)
                                        settings.hiddenTags.reset()
                                        settings.metricsToHide.reset()
                                    }}
                                    subject_uuid={subject_uuid}
                                    visibleDetailsTabs={settings.visibleDetailsTabs}
                                />
                            }
                            expanded={settings.visibleDetailsTabs.value.filter((tab) => tab?.startsWith(metric_uuid)).length > 0}
                            id={metric_uuid}
                            onExpand={(expand) => expandVisibleDetailsTab(expand, metric_uuid, settings.visibleDetailsTabs)}
                            style={style}
                        >
                            <Table.Cell style={style}>{metricName}</Table.Cell>
                            {nrDates > 1 && <MeasurementCells dates={dates} metric={metric} metric_uuid={metric_uuid} measurements={reversedMeasurements} />}
                            {nrDates === 1 && !settings.hiddenColumns.includes("trend") && <Table.Cell><TrendSparkline measurements={metric.recent_measurements} report_date={reportDate} scale={metric.scale} /></Table.Cell>}
                            {nrDates === 1 && !settings.hiddenColumns.includes("status") && <Table.Cell textAlign='center'><StatusIcon status={metric.status} status_start={metric.status_start} /></Table.Cell>}
                            {nrDates === 1 && !settings.hiddenColumns.includes("measurement") && <Table.Cell textAlign="right"><MeasurementValue metric={metric} reportDate={reportDate} /></Table.Cell>}
                            {nrDates === 1 && !settings.hiddenColumns.includes("target") && <Table.Cell textAlign="right"><MeasurementTarget metric={metric} /></Table.Cell>}
                            {!settings.hiddenColumns.includes("unit") && <Table.Cell style={style}>{unit}</Table.Cell>}
                            {!settings.hiddenColumns.includes("source") && <Table.Cell style={style}><MeasurementSources metric={metric} /></Table.Cell>}
                            {!settings.hiddenColumns.includes("time_left") && <Table.Cell style={style}><TimeLeft metric={metric} report={report} /></Table.Cell>}
                            {nrDates > 1 && !settings.hiddenColumns.includes("overrun") && <Table.Cell style={style}><Overrun metric={metric} metric_uuid={metric_uuid} report={report} measurements={measurements} dates={dates} /></Table.Cell>}
                            {!settings.hiddenColumns.includes("comment") && <Table.Cell style={style}><div style={{wordBreak: "break-word"}} dangerouslySetInnerHTML={{ __html: metric.comment }} /></Table.Cell>}
                            {!settings.hiddenColumns.includes("issues") && <Table.Cell style={style}>
                                <IssueStatus metric={metric} issueTrackerMissing={!report.issue_tracker} settings={settings} />
                            </Table.Cell>}
                            {!settings.hiddenColumns.includes("tags") && <Table.Cell style={style}>{getMetricTags(metric).map((tag) => <Tag key={tag} tag={tag} />)}</Table.Cell>}
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
                stopFilteringAndSorting={() => {
                    handleSort(null)
                    settings.hiddenTags.reset()
                    settings.metricsToHide.reset()
                }}
            />
        </Table>
    )
}
SubjectTable.propTypes = {
    changed_fields: stringsPropType,
    dates: datesPropType,
    handleSort: PropTypes.func,
    measurements: PropTypes.array,
    metricEntries: PropTypes.array,
    reload: PropTypes.func,
    report: reportPropType,
    reportDate: optionalDatePropType,
    reports: reportsPropType,
    settings: settingsPropType,
    subject: PropTypes.object,
    subject_uuid: PropTypes.string
}
