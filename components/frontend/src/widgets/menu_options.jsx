import { getMetricName, getSourceName, getSubjectName, getSubjectTypeMetrics } from "../utils"
import { ItemBreadcrumb } from "./ItemBreadcrumb"

function sortOptions(options) {
    return options.sort((a, b) => a.text.localeCompare(b.text))
}

export function metricOptions(reports, dataModel, currentSubjectType, currentSubjectUuid) {
    const subjectMetrics = getSubjectTypeMetrics(currentSubjectType, dataModel.subjects)
    let options = []
    for (const report of reports) {
        for (const [subjectUuid, subject] of Object.entries(report.subjects)) {
            if (subjectUuid === currentSubjectUuid) {
                continue
            }
            const subjectName = getSubjectName(subject, dataModel)
            for (const [metricUuid, metric] of Object.entries(subject.metrics)) {
                if (!subjectMetrics.includes(metric.type)) {
                    continue
                }
                const metricName = getMetricName(metric, dataModel)
                options.push({
                    content: <ItemBreadcrumb report={report.title} subject={subjectName} metric={metricName} />,
                    key: metricUuid,
                    text: report.title + subjectName + metricName,
                    value: metricUuid,
                })
            }
        }
    }
    return sortOptions(options)
}

export function reportOptions(reports) {
    return sortOptions(
        reports.map((report) => ({
            key: report.report_uuid,
            content: report.title,
            text: report.title,
            value: report.report_uuid,
        })),
    )
}

export function sourceOptions(reports, dataModel, currentMetricType, currentMetricUuid) {
    const metricSources = dataModel.metrics[currentMetricType].sources
    let options = []
    reports.forEach((report) => {
        Object.values(report.subjects).forEach((subject) => {
            const subjectName = getSubjectName(subject, dataModel)
            Object.entries(subject.metrics).forEach(([metricUuid, metric]) => {
                if (metricUuid === currentMetricUuid) {
                    return
                }
                const metricName = getMetricName(metric, dataModel)
                Object.entries(metric.sources).forEach(([sourceUuid, source]) => {
                    if (!metricSources.includes(source.type)) {
                        return
                    }
                    const sourceName = getSourceName(source, dataModel)
                    options.push({
                        content: (
                            <ItemBreadcrumb
                                report={report.title}
                                subject={subjectName}
                                metric={metricName}
                                source={sourceName}
                            />
                        ),
                        key: sourceUuid,
                        text: report.title + subjectName + metricName + sourceName,
                        value: sourceUuid,
                    })
                })
            })
        })
    })
    return sortOptions(options)
}

export function subjectOptions(reports, dataModel, currentReportUuid) {
    let options = []
    reports.forEach((report) => {
        if (report.report_uuid === currentReportUuid) {
            return
        }
        Object.entries(report.subjects).forEach(([subjectUuid, subject]) => {
            const subjectName = getSubjectName(subject, dataModel)
            options.push({
                content: <ItemBreadcrumb report={report.title} subject={subjectName} />,
                key: subjectUuid,
                text: report.title + subjectName,
                value: subjectUuid,
            })
        })
    })
    return sortOptions(options)
}
