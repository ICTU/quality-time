import { func } from "prop-types"
import { useContext } from "react"

import { setReportAttribute } from "../api/report"
import { DataModel } from "../context/DataModel"
import { CardDashboard } from "../dashboard/CardDashboard"
import { IssuesCard } from "../dashboard/IssuesCard"
import { LegendCard } from "../dashboard/LegendCard"
import { MetricsRequiringActionCard } from "../dashboard/MetricsRequiringActionCard"
import { MetricSummaryCard } from "../dashboard/MetricSummaryCard"
import { datesPropType, measurementsPropType, reportPropType, settingsPropType } from "../sharedPropTypes"
import { getReportTags, getSubjectName, nrMetricsInReport, sum, visibleMetrics } from "../utils"
import { Tag } from "../widgets/Tag"
import { summarizeMetricsOnDate, summarizeReportOnDate } from "./report_utils"

export function ReportDashboard({ dates, measurements, onClick, onClickTag, reload, report, settings }) {
    const dataModel = useContext(DataModel)
    const nrMetrics = Math.max(nrMetricsInReport(report), 1)
    const subjectCards = []
    if (settings.hiddenCards.excludes("subjects")) {
        for (const [subjectUuid, subject] of Object.entries(report.subjects)) {
            const metrics = visibleMetrics(subject.metrics, settings.metricsToHide.value, settings.hiddenTags.value)
            if (Object.keys(metrics).length > 0) {
                const summary = {}
                for (const date of dates) {
                    summary[date] = summarizeMetricsOnDate(dataModel, date, measurements, metrics)
                }
                subjectCards.push(
                    <MetricSummaryCard
                        header={getSubjectName(report.subjects[subjectUuid], dataModel)}
                        key={subjectUuid}
                        maxY={nrMetrics}
                        onClick={(event) => onClick(event, subjectUuid)}
                        summary={summary}
                    />,
                )
            }
        }
    }
    let tagCards = []
    if (settings.hiddenCards.excludes("tags")) {
        const anyTagsHidden = settings.hiddenTags.value.length > 0
        getReportTags(report, settings.hiddenTags.value).forEach((tag) => {
            const summary = {}
            dates.forEach((date) => {
                summary[date] = summarizeReportOnDate(dataModel, settings, report, measurements, date, tag)
            })
            if (Object.values(summary).every((summaryOnDate) => sum(summaryOnDate) === 0)) {
                return // Don't show a tag card when all metrics with the tag have been hidden
            }
            tagCards.push(
                <MetricSummaryCard
                    header={<Tag selected={anyTagsHidden} tag={tag} />}
                    key={tag}
                    maxY={nrMetrics}
                    onClick={() => onClickTag(tag)}
                    selected={anyTagsHidden}
                    summary={summary}
                />,
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
                setReportAttribute(report.report_uuid, "layout", newLayout, reload)
            }}
        />
    )
}
ReportDashboard.propTypes = {
    dates: datesPropType,
    measurements: measurementsPropType,
    onClick: func,
    onClickTag: func,
    reload: func,
    report: reportPropType,
    settings: settingsPropType,
}
