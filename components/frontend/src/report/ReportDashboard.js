import { array, func } from "prop-types"
import { useContext } from "react"

import { set_report_attribute } from "../api/report"
import { DataModel } from "../context/DataModel"
import { CardDashboard } from "../dashboard/CardDashboard"
import { LegendCard } from "../dashboard/LegendCard"
import { MetricSummaryCard } from "../dashboard/MetricSummaryCard"
import { datesPropType, reportPropType, settingsPropType } from "../sharedPropTypes"
import {
    get_subject_name,
    getMetricTags,
    getReportTags,
    nrMetricsInReport,
    STATUS_COLORS,
    visibleMetrics,
} from "../utils"
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
    if (!settings.hiddenCards.includes("subjects")) {
        Object.entries(report.subjects).forEach(([subject_uuid, subject]) => {
            const metrics = visibleMetrics(subject.metrics, "none", settings.hiddenTags.value)
            if (Object.keys(metrics).length > 0) {
                const summary = {}
                dates.forEach((date) => {
                    summary[date] = summarizeMetricsOnDate(metrics, measurements, date, dataModel)
                })
                subjectCards.push(
                    <MetricSummaryCard
                        header={get_subject_name(report.subjects[subject_uuid], dataModel)}
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
    if (!settings.hiddenCards.includes("tags")) {
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
                    summary={summary}
                />
            )
        })
    }
    return (
        <CardDashboard
            cards={subjectCards.concat(tagCards.concat([<LegendCard key="legend" />]))}
            initialLayout={report.layout}
            saveLayout={function (newLayout) {
                set_report_attribute(report.report_uuid, "layout", newLayout, reload)
            }}
        />
    )
}
ReportDashboard.propTypes = {
    dates: datesPropType,
    measurements: array,
    onClick: func,
    onClickTag: func,
    reload: func,
    report: reportPropType,
    settings: settingsPropType,
}
