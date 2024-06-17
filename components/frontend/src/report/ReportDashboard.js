import { func } from "prop-types"
import { useContext } from "react"

import { set_report_attribute } from "../api/report"
import { DataModel } from "../context/DataModel"
import { CardDashboard } from "../dashboard/CardDashboard"
import { IssuesCard } from "../dashboard/IssuesCard"
import { LegendCard } from "../dashboard/LegendCard"
import { MetricsRequiringActionCard } from "../dashboard/MetricsRequiringActionCard"
import { MetricSummaryCard } from "../dashboard/MetricSummaryCard"
import { STATUS_COLORS } from "../metric/status"
import { datesPropType, measurementPropType, reportPropType, settingsPropType } from "../sharedPropTypes"
import { getMetricTags, getReportTags, getSubjectName, nrMetricsInReport, visibleMetrics } from "../utils"
import { Tag } from "../widgets/Tag"
import { metricStatusOnDate } from "./report_utils"

function summarizeMetricsOnDate(metrics, measurements, date, dataModel) {
    const summary = { red: 0, yellow: 0, green: 0, blue: 0, grey: 0, white: 0 }
    Object.entries(metrics).forEach(([metric_uuid, metric]) => {
        const status = metricStatusOnDate(metric_uuid, metric, measurements, date, dataModel)
        summary[STATUS_COLORS[status]] += 1
    })
    return summary
}

function summarizeTagOnDate(report, measurements, tag, date, dataModel) {
    const summary = { red: 0, yellow: 0, green: 0, blue: 0, grey: 0, white: 0 }
    Object.values(report.subjects).forEach((subject) => {
        Object.entries(subject.metrics).forEach(([metric_uuid, metric]) => {
            if (getMetricTags(metric).indexOf(tag) >= 0) {
                const status = metricStatusOnDate(metric_uuid, metric, measurements, date, dataModel)
                summary[STATUS_COLORS[status]] += 1
            }
        })
    })
    return summary
}

export function ReportDashboard({ dates, measurements, onClick, onClickTag, reload, report, settings }) {
    const dataModel = useContext(DataModel)
    const nrMetrics = Math.max(nrMetricsInReport(report), 1)
    const subjectCards = []
    if (settings.hiddenCards.excludes("subjects")) {
        Object.entries(report.subjects).forEach(([subject_uuid, subject]) => {
            const metrics = visibleMetrics(subject.metrics, "none", settings.hiddenTags.value)
            if (Object.keys(metrics).length > 0) {
                const summary = {}
                dates.forEach((date) => {
                    summary[date] = summarizeMetricsOnDate(metrics, measurements, date, dataModel)
                })
                subjectCards.push(
                    <MetricSummaryCard
                        header={getSubjectName(report.subjects[subject_uuid], dataModel)}
                        key={subject_uuid}
                        maxY={nrMetrics}
                        onClick={(event) => onClick(event, subject_uuid)}
                        summary={summary}
                    />,
                )
            }
        })
    }
    let tagCards = []
    if (settings.hiddenCards.excludes("tags")) {
        const anyTagsHidden = settings.hiddenTags.value.length > 0
        tagCards = getReportTags(report, settings.hiddenTags.value).map((tag) => {
            const summary = {}
            dates.forEach((date) => {
                summary[date] = summarizeTagOnDate(report, measurements, tag, date, dataModel)
            })
            return (
                <MetricSummaryCard
                    header={<Tag selected={anyTagsHidden} tag={tag} />}
                    key={tag}
                    maxY={nrMetrics}
                    onClick={() => onClickTag(tag)}
                    selected={anyTagsHidden}
                    summary={summary}
                />
            )
        })
    }
    const extraCards = []
    if (settings.hiddenCards.excludes("action_required")) {
        const metricRequiringActionSelected = settings.metricsToHide.value === "no_action_required"
        extraCards.push(
            <MetricsRequiringActionCard
                key="metrics_requiring_action"
                reports={[report]}
                onClick={() =>
                    settings.metricsToHide.set(metricRequiringActionSelected ? "none" : "no_action_required")
                }
                selected={metricRequiringActionSelected}
            />,
        )
    }
    if (report.issue_tracker?.type && settings.hiddenCards.excludes("issues")) {
        const selected = settings.metricsToHide.value === "no_issues"
        extraCards.push(
            <IssuesCard
                key="issues"
                onClick={() => settings.metricsToHide.set(selected ? "none" : "no_issues")}
                report={report}
                selected={selected}
            />,
        )
    }
    if (settings.hiddenCards.excludes("legend")) {
        extraCards.push(<LegendCard key="legend" />)
    }
    return (
        <CardDashboard
            cards={subjectCards.concat(tagCards.concat(extraCards))}
            initialLayout={report.layout}
            saveLayout={function (newLayout) {
                set_report_attribute(report.report_uuid, "layout", newLayout, reload)
            }}
        />
    )
}
ReportDashboard.propTypes = {
    dates: datesPropType,
    measurements: measurementPropType,
    onClick: func,
    onClickTag: func,
    reload: func,
    report: reportPropType,
    settings: settingsPropType,
}
