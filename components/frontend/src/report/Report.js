import React, { useContext } from 'react';
import PropTypes from 'prop-types';
import { Message } from 'semantic-ui-react';
import { datePropType, datesPropType, issueSettingsPropType, sortDirectionPropType } from '../sharedPropTypes';
import { DataModel } from '../context/DataModel';
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { Subjects } from '../subject/Subjects';
import { CommentSegment } from '../widgets/CommentSegment';
import { Tag } from '../widgets/Tag';
import { CardDashboard } from '../dashboard/CardDashboard';
import { LegendCard } from '../dashboard/LegendCard';
import { MetricSummaryCard } from '../dashboard/MetricSummaryCard';
import { set_report_attribute } from '../api/report';
import { getReportTags, getMetricTags, nrMetricsInReport, get_subject_name, STATUS_COLORS, visibleMetrics } from '../utils';
import { ReportTitle } from './ReportTitle';
import { metricStatusOnDate } from './report_utils';

function summarizeMetricsOnDate(metrics, measurements, date) {
    const summary = { red: 0, yellow: 0, green: 0, blue: 0, grey: 0, white: 0 }
    Object.entries(metrics).forEach(([metric_uuid, metric]) => {
        const status = metricStatusOnDate(metric_uuid, metric, measurements, date);
        summary[STATUS_COLORS[status]] += 1
    })
    return summary
}

function summarizeTagOnDate(report, measurements, tag, date) {
    const summary = { red: 0, yellow: 0, green: 0, blue: 0, grey: 0, white: 0 }
    Object.values(report.subjects).forEach(subject => {
        Object.entries(subject.metrics).forEach(([metric_uuid, metric]) => {
            if (getMetricTags(metric).indexOf(tag) >= 0) {
                const status = metricStatusOnDate(metric_uuid, metric, measurements, date);
                summary[STATUS_COLORS[status]] += 1
            }
        })
    })
    return summary
}

function ReportDashboard(
    {
        dates,
        hiddenTags,
        hideMetricsNotRequiringAction,
        measurements,
        onClick,
        onClickTag,
        reload,
        report
    }
) {
    const dataModel = useContext(DataModel)
    const nrMetrics = Math.max(nrMetricsInReport(report), 1);
    const subjectCards = []
    Object.entries(report.subjects).forEach(([subject_uuid, subject]) => {
        const metrics = visibleMetrics(subject.metrics, hideMetricsNotRequiringAction, hiddenTags)
        if (Object.keys(metrics).length > 0) {
            const summary = {}
            dates.forEach((date) => {
                summary[date] = summarizeMetricsOnDate(metrics, measurements, date)
            })
            subjectCards.push(
                <MetricSummaryCard
                    header={get_subject_name(report.subjects[subject_uuid], dataModel)}
                    key={subject_uuid}
                    maxY={nrMetrics}
                    onClick={(event) => onClick(event, subject_uuid)}
                    summary={summary}
                />
            )
        }
    })
    const tagCards = getReportTags(report, hiddenTags).map((tag) => {
        const summary = {}
        dates.forEach((date) => {
            summary[date] = summarizeTagOnDate(report, measurements, tag, date)
        })
        return (
            <MetricSummaryCard
                header={<Tag tag={tag} />}
                key={tag}
                maxY={nrMetrics}
                onClick={() => onClickTag(tag)}
                summary={summary}
            />
        )
    })
    return (
        <Permissions.Consumer>{(permissions) => (
            <CardDashboard
                cards={subjectCards.concat(tagCards.concat([<LegendCard key="legend" />]))}
                initialLayout={report.layout}
                saveLayout={function (layout) { if (accessGranted(permissions, [EDIT_REPORT_PERMISSION])) { set_report_attribute(report.report_uuid, "layout", layout, reload) } }}
            />)}
        </Permissions.Consumer>
    )
}
ReportDashboard.propTypes = {
    dates: datesPropType,
    hiddenTags: PropTypes.arrayOf(PropTypes.string),
    hideMetricsNotRequiringAction: PropTypes.bool,
    measurements: PropTypes.array,
    onClick: PropTypes.func,
    onClickTag: PropTypes.func,
    reload: PropTypes.func,
    report: PropTypes.object
}

function ReportErrorMessage({ report_date }) {
    return (
        <Message warning size='huge'>
            <Message.Header>
                {report_date ? `Sorry, this report didn't exist at ${report_date}` : "Sorry, this report doesn't exist"}
            </Message.Header>
        </Message>
    )
}
ReportErrorMessage.propTypes = {
    report_date: datePropType
}

export function Report({
    changed_fields,
    dates,
    go_home,
    handleSort,
    hiddenColumns,
    hiddenTags,
    hideMetricsNotRequiringAction,
    issueSettings,
    measurements,
    reload,
    report,
    report_date,
    reports,
    sortColumn,
    sortDirection,
    toggleHiddenTag,
    toggleVisibleDetailsTab,
    visibleDetailsTabs
}) {

    function navigate_to_subject(event, subject_uuid) {
        event.preventDefault();
        document.getElementById(subject_uuid).scrollIntoView();
        window.scrollBy(0, 163);  // Correct for menubar and subject title margin
    }

    if (!report) {
        return <ReportErrorMessage report_date={report_date} />
    }
    // Sort measurements in reverse order so that if there multiple measurements on a day, we find the most recent one:
    const reversedMeasurements = measurements.slice().sort((m1, m2) => m1.start < m2.start ? 1 : -1)
    return (
        <div id="dashboard">
            <ReportTitle
                go_home={go_home}
                report={report}
                changed_fields={changed_fields}
                reload={reload}
                report_date={report_date}
                reports={reports}
            />
            <CommentSegment comment={report.comment} />
            <ReportDashboard
                dates={dates}
                hiddenTags={hiddenTags}
                hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
                measurements={reversedMeasurements}
                onClick={(e, s) => navigate_to_subject(e, s)}
                onClickTag={(tag) => {
                    const tagsToToggle = hiddenTags?.length > 0 ? hiddenTags : getReportTags(report)
                    toggleHiddenTag(...tagsToToggle.filter((visibleTag) => visibleTag !== tag))
                }}
                report={report}
                reload={reload}
            />
            <Subjects
                changed_fields={changed_fields}
                dates={dates}
                handleSort={handleSort}
                hiddenColumns={hiddenColumns}
                hiddenTags={hiddenTags}
                hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
                issueSettings={issueSettings}
                measurements={measurements}
                reload={reload}
                report={report}
                reports={reports}
                report_date={report_date}
                sortColumn={sortColumn}
                sortDirection={sortDirection}
                toggleVisibleDetailsTab={toggleVisibleDetailsTab}
                visibleDetailsTabs={visibleDetailsTabs}
            />
        </div>
    )
}
Report.propTypes = {
    changed_fields: PropTypes.arrayOf(PropTypes.string),
    dates: datesPropType,
    go_home: PropTypes.func,
    handleSort: PropTypes.func,
    hiddenColumns: PropTypes.arrayOf(PropTypes.string),
    hiddenTags: PropTypes.arrayOf(PropTypes.string),
    hideMetricsNotRequiringAction: PropTypes.bool,
    issueSettings: issueSettingsPropType,
    measurements: PropTypes.array,
    reload: PropTypes.func,
    report: PropTypes.object,
    report_date: datePropType,
    reports: PropTypes.array,
    sortColumn: PropTypes.string,
    sortDirection: sortDirectionPropType,
    toggleHiddenTag: PropTypes.func,
    toggleVisibleDetailsTab: PropTypes.func,
    visibleDetailsTabs: PropTypes.arrayOf(PropTypes.string)
}
