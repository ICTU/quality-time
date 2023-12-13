
import React, { useContext } from 'react';
import PropTypes from 'prop-types';
import { datesPropType, reportPropType, settingsPropType } from '../sharedPropTypes';
import { DataModel } from '../context/DataModel';
import { Tag } from '../widgets/Tag';
import { CardDashboard } from '../dashboard/CardDashboard';
import { LegendCard } from '../dashboard/LegendCard';
import { MetricSummaryCard } from '../dashboard/MetricSummaryCard';
import { set_report_attribute } from '../api/report';
import { getReportTags, getMetricTags, nrMetricsInReport, get_subject_name, STATUS_COLORS, visibleMetrics } from '../utils';
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

export function ReportDashboard(
    {
        dates,
        measurements,
        onClick,
        onClickTag,
        reload,
        report,
        settings,
    }
) {
    const dataModel = useContext(DataModel)
    const nrMetrics = Math.max(nrMetricsInReport(report), 1);
    const subjectCards = []
    Object.entries(report.subjects).forEach(([subject_uuid, subject]) => {
        const metrics = visibleMetrics(subject.metrics, "none", settings.hiddenTags.value)
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
    const anyTagsHidden = settings.hiddenTags.value.length > 0
    const tagCards = getReportTags(report, settings.hiddenTags.value).map((tag) => {
        const summary = {}
        dates.forEach((date) => {
            summary[date] = summarizeTagOnDate(report, measurements, tag, date)
        })
        return (
            <MetricSummaryCard
                header={<Tag selected={anyTagsHidden} tag={tag} />}
                key={tag}
                maxY={nrMetrics}
                onClick={() => onClickTag(tag)}
                summary={summary}
            />
        )
    })
    return (
        <CardDashboard
            cards={subjectCards.concat(tagCards.concat([<LegendCard key="legend" />]))}
            initialLayout={report.layout}
            saveLayout={function (new_layout) { set_report_attribute(report.report_uuid, "layout", new_layout, reload) }}
        />
    )
}
ReportDashboard.propTypes = {
    dates: datesPropType,
    measurements: PropTypes.array,
    onClick: PropTypes.func,
    onClickTag: PropTypes.func,
    reload: PropTypes.func,
    report: reportPropType,
    settings: settingsPropType
}
