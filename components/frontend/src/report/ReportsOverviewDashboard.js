import { array, func } from "prop-types"
import { useContext } from "react"

import { set_reports_attribute } from "../api/report"
import { DataModel } from "../context/DataModel"
import { CardDashboard } from "../dashboard/CardDashboard"
import { LegendCard } from "../dashboard/LegendCard"
import { MetricsRequiringActionCard } from "../dashboard/MetricsRequiringActionCard"
import { MetricSummaryCard } from "../dashboard/MetricSummaryCard"
import { datesPropType, measurementsPropType, reportsPropType, settingsPropType } from "../sharedPropTypes"
import { getReportsTags, nrMetricsInReport, sum } from "../utils"
import { Tag } from "../widgets/Tag"
import { summarizeReportOnDate, summarizeReportsOnDate } from "./report_utils"

export function ReportsOverviewDashboard({
    dates,
    layout,
    measurements,
    onClickTag,
    openReport,
    reports,
    reload,
    settings,
}) {
    const dataModel = useContext(DataModel)
    let nrMetrics = 0
    const reportSummary = {}
    reports.forEach((report) => {
        nrMetrics = Math.max(nrMetrics, nrMetricsInReport(report))
        reportSummary[report.report_uuid] = {}
        dates.forEach((date) => {
            reportSummary[report.report_uuid][date] = summarizeReportOnDate(
                dataModel,
                settings,
                report,
                measurements,
                date,
            )
        })
    })
    const tagSummary = {}
    const tags = getReportsTags(reports, settings.hiddenTags.value)
    tags.forEach((tag) => {
        tagSummary[tag] = {}
        dates.forEach((date) => {
            tagSummary[tag][date] = summarizeReportsOnDate(dataModel, settings, reports, measurements, date, tag)
            nrMetrics = Math.max(nrMetrics, sum(tagSummary[tag][date]))
        })
    })
    let report_cards = []
    if (settings.hiddenCards.excludes("reports")) {
        report_cards = reports.map((report) => (
            <MetricSummaryCard
                key={report.report_uuid}
                header={report.title}
                maxY={nrMetrics}
                onClick={(event) => {
                    event.preventDefault()
                    openReport(report.report_uuid)
                }}
                summary={reportSummary[report.report_uuid]}
            />
        ))
    }
    let tagCards = []
    if (settings.hiddenCards.excludes("tags")) {
        const anyTagsHidden = settings.hiddenTags.value.length > 0
        tagCards = tags
            .filter((tag) => settings.hiddenTags.excludes(tag))
            .map((tag) => (
                <MetricSummaryCard
                    key={tag}
                    header={<Tag selected={anyTagsHidden} tag={tag} />}
                    maxY={nrMetrics}
                    onClick={() => onClickTag(tag)}
                    summary={tagSummary[tag]}
                />
            ))
    }
    let extraCards = []
    if (settings.hiddenCards.excludes("action_required")) {
        const metricRequiringActionSelected = settings.metricsToHide.value === "no_action_required"
        extraCards.push(
            <MetricsRequiringActionCard
                key="metrics_requiring_action"
                reports={reports}
                onClick={() => settings.metricsToHide.set(metricRequiringActionSelected ? "all" : "no_action_required")}
                selected={metricRequiringActionSelected}
            />,
        )
    }
    if (settings.hiddenCards.excludes("legend")) {
        extraCards.push(<LegendCard key="legend" />)
    }
    return (
        <CardDashboard
            cards={report_cards.concat(tagCards).concat(extraCards)}
            initialLayout={layout}
            saveLayout={function (new_layout) {
                set_reports_attribute("layout", new_layout, reload)
            }}
        />
    )
}
ReportsOverviewDashboard.propTypes = {
    dates: datesPropType,
    layout: array,
    measurements: measurementsPropType,
    onClickTag: func,
    openReport: func,
    reload: func,
    reports: reportsPropType,
    settings: settingsPropType,
}
