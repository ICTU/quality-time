import React from 'react';
import { Message } from 'semantic-ui-react';
import { Segment } from '../semantic_ui_react_wrappers';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { CardDashboard } from '../dashboard/CardDashboard';
import { LegendCard } from '../dashboard/LegendCard';
import { MetricSummaryCard } from '../dashboard/MetricSummaryCard';
import { CommentSegment } from '../widgets/CommentSegment';
import { Tag } from '../widgets/Tag';
import { add_report, set_reports_attribute, copy_report } from '../api/report';
import { ReportsOverviewTitle } from './ReportsOverviewTitle';
import { AddButton, CopyButton } from '../widgets/Button';
import { report_options } from '../widgets/menu_options';
import { getMetricTags, getReportsTags, nrMetricsInReport, STATUS_COLORS, sum } from '../utils';
import { metricStatusOnDate } from './report_utils';

function summarizeReportOnDate(report, measurements, date) {
    const summary = { red: 0, yellow: 0, green: 0, blue: 0, grey: 0, white: 0 }
    Object.values(report.subjects).forEach((subject) => {
        Object.entries(subject.metrics).forEach(([metric_uuid, metric]) => {
            const status = metricStatusOnDate(metric_uuid, metric, measurements, date)
            summary[STATUS_COLORS[status]] += 1
        })
    })
    return summary
}

function summarizeReportsOnDate(reports, measurements, date, tag) {
    const summary = { red: 0, yellow: 0, green: 0, blue: 0, grey: 0, white: 0 }
    reports.forEach((report) => {
        Object.values(report.subjects).forEach(subject => {
            Object.entries(subject.metrics).forEach(([metric_uuid, metric]) => {
                if (getMetricTags(metric).indexOf(tag) >= 0) {
                    const status = metricStatusOnDate(metric_uuid, metric, measurements, date)
                    summary[STATUS_COLORS[status]] += 1
                }
            })
        })
    })
    return summary
}


function ReportsDashboard({ dates, reports, open_report, measurements, layout, reload }) {
    let nrMetrics = 0
    const reportSummary = {}
    reports.forEach((report) => {
        nrMetrics = Math.max(nrMetrics, nrMetricsInReport(report))
        reportSummary[report.report_uuid] = {}
        dates.forEach((date) => {
            reportSummary[report.report_uuid][date] = summarizeReportOnDate(report, measurements, date)
        })
    })
    const tagSummary = {}
    const tags = getReportsTags(reports)
    tags.forEach((tag) => {
        tagSummary[tag] = {}
        dates.forEach((date) => {
            tagSummary[tag][date] = summarizeReportsOnDate(reports, measurements, date, tag)
            nrMetrics = Math.max(nrMetrics, sum(tagSummary[tag][date]))
        })
    })
    const report_cards = reports.map((report) =>
        <MetricSummaryCard
            key={report.report_uuid}
            header={report.title}
            maxY={nrMetrics}
            onClick={(e) => open_report(e, report.report_uuid)}
            summary={reportSummary[report.report_uuid]}
        />
    );
    const tag_cards = tags.map((tag) =>
        <MetricSummaryCard
            key={tag}
            header={<Tag tag={tag} />}
            maxY={nrMetrics}
            onClick={(e) => open_report(e, `tag-${tag}`)}
            summary={tagSummary[tag]}
        />
    );
    return (
        <CardDashboard
            cards={report_cards.concat(tag_cards).concat([<LegendCard key="legend" />])}
            initial_layout={layout || []}
            save_layout={function (new_layout) { set_reports_attribute("layout", new_layout, reload) }}
        />
    )
}

export function ReportsOverview({ dates, measurements, reports, open_report, report_date, reports_overview, reload }) {
    if (reports.length === 0 && report_date !== null) {
        return (
            <Message warning size='huge'>
                <Message.Header>
                    {`Sorry, no reports existed at ${report_date}`}
                </Message.Header>
            </Message>
        )
    }
    // Sort measurements in reverse order so that if there multiple measurements on a day, we find the most recent one:
    const reversedMeasurements = measurements.slice().sort((m1, m2) => m1.start < m2.start ? 1 : -1)
    return (
        <div id="dashboard">
            <ReportsOverviewTitle reports_overview={reports_overview} reload={reload} />
            <CommentSegment comment={reports_overview.comment} />
            <ReportsDashboard dates={dates} measurements={reversedMeasurements} reports={reports} open_report={open_report} layout={reports_overview.layout} reload={reload} />
            <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
                <Segment basic>
                    <AddButton
                        item_type={"report"}
                        onClick={() => add_report(reload)}
                    />
                    <CopyButton
                        item_type={"report"}
                        get_options={() => report_options(reports)}
                        onChange={(source_report_uuid) => copy_report(source_report_uuid, reload)}
                    />
                </Segment>
            }
            />
        </div>
    )
}
