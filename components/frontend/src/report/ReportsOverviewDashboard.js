import React from 'react';
import PropTypes from 'prop-types';
import { CardDashboard } from '../dashboard/CardDashboard';
import { LegendCard } from '../dashboard/LegendCard';
import { MetricSummaryCard } from '../dashboard/MetricSummaryCard';
import { Tag } from '../widgets/Tag';
import { set_reports_attribute } from '../api/report';
import { getMetricTags, getReportsTags, nrMetricsInReport, STATUS_COLORS, sum, visibleMetrics } from '../utils';
import {
    datesPropType,
    reportsPropType,
    settingsPropType,
} from '../sharedPropTypes';
import { metricStatusOnDate } from './report_utils';

function summarizeReportOnDate(report, measurements, date, hiddenTags) {
    const summary = { red: 0, yellow: 0, green: 0, blue: 0, grey: 0, white: 0 }
    Object.values(report.subjects).forEach((subject) => {
        const metrics = visibleMetrics(subject.metrics, "none", hiddenTags)
        Object.entries(metrics).forEach(([metric_uuid, metric]) => {
            const status = metricStatusOnDate(metric_uuid, metric, measurements, date)
            summary[STATUS_COLORS[status]] += 1
        })
    })
    return summary
}

function summarizeReportsOnDate(reports, measurements, date, tag, hiddenTags) {
    const summary = { red: 0, yellow: 0, green: 0, blue: 0, grey: 0, white: 0 }
    reports.forEach((report) => {
        Object.values(report.subjects).forEach(subject => {
            const metrics = visibleMetrics(subject.metrics, "none", hiddenTags)
            Object.entries(metrics).forEach(([metric_uuid, metric]) => {
                if (getMetricTags(metric).indexOf(tag) >= 0) {
                    const status = metricStatusOnDate(metric_uuid, metric, measurements, date)
                    summary[STATUS_COLORS[status]] += 1
                }
            })
        })
    })
    return summary
}

export function ReportsOverviewDashboard(
    {
        dates,
        layout,
        measurements,
        onClickTag,
        openReport,
        reports,
        reload,
        settings
    }
) {
    let nrMetrics = 0
    const reportSummary = {}
    reports.forEach((report) => {
        nrMetrics = Math.max(nrMetrics, nrMetricsInReport(report))
        reportSummary[report.report_uuid] = {}
        dates.forEach((date) => {
            reportSummary[report.report_uuid][date] = summarizeReportOnDate(report, measurements, date, settings.hiddenTags.value)
        })
    })
    const tagSummary = {}
    const tags = getReportsTags(reports, settings.hiddenTags.value)
    tags.forEach((tag) => {
        tagSummary[tag] = {}
        dates.forEach((date) => {
            tagSummary[tag][date] = summarizeReportsOnDate(reports, measurements, date, tag, settings.hiddenTags.value)
            nrMetrics = Math.max(nrMetrics, sum(tagSummary[tag][date]))
        })
    })
    let report_cards = []
    if (!settings.hiddenCards.includes("reports")) {
        report_cards = reports.map((report) =>
            <MetricSummaryCard
                key={report.report_uuid}
                header={report.title}
                maxY={nrMetrics}
                onClick={(event) => { event.preventDefault(); openReport(report.report_uuid) }}
                summary={reportSummary[report.report_uuid]}
            />
        );
    }
    let tagCards = []
    if (!settings.hiddenCards.includes("tags")) {
        const anyTagsHidden = settings.hiddenTags.value.length > 0
        tagCards = tags.filter((tag) => (!settings.hiddenTags.includes(tag))).map((tag) =>
            <MetricSummaryCard
                key={tag}
                header={<Tag selected={anyTagsHidden} tag={tag} />}
                maxY={nrMetrics}
                onClick={() => onClickTag(tag)}
                summary={tagSummary[tag]}
            />
        );
    }
    return (
        <CardDashboard
            cards={report_cards.concat(tagCards).concat([<LegendCard key="legend" />])}
            initialLayout={layout}
            saveLayout={function (new_layout) { set_reports_attribute("layout", new_layout, reload) }}
        />
    )
}
ReportsOverviewDashboard.propTypes = {
    dates: datesPropType,
    layout: PropTypes.array,
    measurements: PropTypes.array,
    onClickTag: PropTypes.func,
    openReport: PropTypes.func,
    reload: PropTypes.func,
    reports: reportsPropType,
    settings: settingsPropType
}
