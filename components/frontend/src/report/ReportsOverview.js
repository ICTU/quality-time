import React, { useEffect, useState } from 'react';
import { Message } from 'semantic-ui-react';
import { Segment } from '../semantic_ui_react_wrappers';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { CardDashboard } from '../dashboard/CardDashboard';
import { LegendCard } from '../dashboard/LegendCard';
import { MetricSummaryCard } from '../dashboard/MetricSummaryCard';
import { CommentSegment } from '../widgets/CommentSegment';
import { Tag } from '../widgets/Tag';
import { add_report, get_reports_overview_measurements, set_reports_attribute, copy_report } from '../api/report';
import { ReportsOverviewTitle } from './ReportsOverviewTitle';
import { AddButton, CopyButton } from '../widgets/Button';
import { report_options } from '../widgets/menu_options';
import { getMetricTags, getReportsTags, nrMetricsInReport, STATUS_COLORS } from '../utils';
import { metricStatusOnDate } from './report_utils';

function summarizeReportOnDate(report, measurements, date) {
    const isoDateString = date.toISOString().split("T")[0];
    const summary = { red: 0, yellow: 0, green: 0, blue: 0, grey: 0, white: 0 }
    Object.values(report.subjects).forEach((subject) => {
        Object.entries(subject.metrics).forEach(([metric_uuid, metric]) => {
            const status = metricStatusOnDate(metric_uuid, metric, measurements, isoDateString)
            summary[STATUS_COLORS[status]] += 1
        })
    })
    return summary
}

function summarizeReportsOnDate(reports, measurements, date, tag) {
    const isoDateString = date.toISOString().split("T")[0];
    const summary = { red: 0, yellow: 0, green: 0, blue: 0, grey: 0, white: 0 }
    reports.forEach((report) => {
        Object.values(report.subjects).forEach(subject => {
            Object.entries(subject.metrics).forEach(([metric_uuid, metric]) => {
                if (getMetricTags(metric).indexOf(tag) >= 0) {
                    const status = metricStatusOnDate(metric_uuid, metric, measurements, isoDateString)
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
            const sum = Object.values(tagSummary[tag][date]).reduce((a, b) => a + b, 0)
            nrMetrics = Math.max(nrMetrics, sum)
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

export function ReportsOverview({ dates, reports, open_report, report_date, reports_overview, reload }) {
    const [measurements, setMeasurements] = useState([]);
    useEffect(() => {
        if (reports.length > 0 && dates.length > 0) {
            const minReportDate = dates.slice().sort((d1, d2) => { return d1.getTime() - d2.getTime() }).at(0);
            get_reports_overview_measurements(report_date, minReportDate).then(json => {
                setMeasurements(json.measurements ?? [])
            })
        }
        // eslint-disable-next-line
    }, [dates, report_date]);

    if (reports.length === 0 && report_date !== null) {
        return (
            <Message warning size='huge'>
                <Message.Header>
                    {`Sorry, no reports existed at ${report_date}`}
                </Message.Header>
            </Message>
        )
    }
    return (
        <div id="dashboard">
            <ReportsOverviewTitle reports_overview={reports_overview} reload={reload} />
            <CommentSegment comment={reports_overview.comment} />
            <ReportsDashboard dates={dates} measurements={measurements} reports={reports} open_report={open_report} layout={reports_overview.layout} reload={reload} />
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
