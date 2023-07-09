import React, { useContext, useEffect, useState } from 'react';
import { Message } from 'semantic-ui-react';
import { DataModel } from '../context/DataModel';
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { Subjects } from '../subject/Subjects';
import { CommentSegment } from '../widgets/CommentSegment';
import { Tag } from '../widgets/Tag';
import { CardDashboard } from '../dashboard/CardDashboard';
import { LegendCard } from '../dashboard/LegendCard';
import { MetricSummaryCard } from '../dashboard/MetricSummaryCard';
import { set_report_attribute } from '../api/report';
import { getReportTags, getMetricTags, nrMetricsInReport, get_subject_name, STATUS_COLORS } from '../utils';
import { ReportTitle } from './ReportTitle';
import { metricStatusOnDate } from './report_utils';

function summarizeSubjectOnDate(subject, measurements, date) {
    const summary = { red: 0, yellow: 0, green: 0, blue: 0, grey: 0, white: 0 }
    Object.entries(subject.metrics).forEach(([metric_uuid, metric]) => {
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

function ReportDashboard({ dates, measurements, report, onClick, setSelectedTags, selectedTags, reload }) {
    const dataModel = useContext(DataModel)
    const nrMetrics = Math.max(nrMetricsInReport(report), 1);
    function subject_cards() {
        return Object.entries(report.subjects).map(([subject_uuid, subject]) => {
            const summary = {}
            dates.forEach((date) => {
                summary[date] = summarizeSubjectOnDate(subject, measurements, date)
            })
            return (
                <MetricSummaryCard
                    header={get_subject_name(report.subjects[subject_uuid], dataModel)}
                    key={subject_uuid}
                    maxY={nrMetrics}
                    onClick={(event) => onClick(event, subject_uuid)}
                    summary={summary}
                />
            )
        });
    }
    function tag_cards() {
        return getReportTags(report).map((tag) => {
            const summary = {}
            dates.forEach((date) => {
                summary[date] = summarizeTagOnDate(report, measurements, tag, date)
            })
            return (
                <MetricSummaryCard
                    header={<Tag tag={tag} selected={selectedTags.includes(tag)} />}
                    key={tag}
                    maxY={nrMetrics}
                    onClick={() => setSelectedTags(tag_list => (tag_list.includes(tag) ? tag_list.filter((value) => value !== tag) : [tag, ...tag_list]))}
                    summary={summary}
                />
            )
        })
    }
    return (
        <Permissions.Consumer>{(permissions) => (
            <CardDashboard
                cards={subject_cards().concat(tag_cards().concat([<LegendCard key="legend" />]))}
                initial_layout={report.layout || []}
                save_layout={function (layout) { if (accessGranted(permissions, [EDIT_REPORT_PERMISSION])) { set_report_attribute(report.report_uuid, "layout", layout, reload) } }}
            />)}
        </Permissions.Consumer>
    )
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

export function Report({
    changed_fields,
    dates,
    go_home,
    handleSort,
    hiddenColumns,
    hideMetricsNotRequiringAction,
    issueSettings,
    measurements,
    reload,
    report,
    report_date,
    reports,
    sortColumn,
    sortDirection,
    toggleVisibleDetailsTab,
    visibleDetailsTabs
}) {

    function navigate_to_subject(event, subject_uuid) {
        event.preventDefault();
        document.getElementById(subject_uuid).scrollIntoView();
        window.scrollBy(0, 163);  // Correct for menubar and subject title margin
    }

    const [selectedTags, setSelectedTags] = useState([]);
    useEffect(() => {
        // Make sure we only filter by tags that are actually used in this report
        setSelectedTags(prev_tags => prev_tags.filter(tag => getReportTags(report).includes(tag)))
    }, [report]);

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
                measurements={reversedMeasurements}
                onClick={(e, s) => navigate_to_subject(e, s)}
                setSelectedTags={setSelectedTags}
                selectedTags={selectedTags}
                report={report}
                reload={reload}
            />
            <Subjects
                changed_fields={changed_fields}
                dates={dates}
                handleSort={handleSort}
                hiddenColumns={hiddenColumns}
                hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
                issueSettings={issueSettings}
                measurements={measurements}
                reload={reload}
                report={report}
                reports={reports}
                report_date={report_date}
                sortColumn={sortColumn}
                sortDirection={sortDirection}
                tags={selectedTags}
                toggleVisibleDetailsTab={toggleVisibleDetailsTab}
                visibleDetailsTabs={visibleDetailsTabs}
            />
        </div>
    )
}
