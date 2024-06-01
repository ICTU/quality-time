import { getMetricName, getSourceName, getSubjectName, getSubjectTypeMetrics } from "../utils"
import { ItemBreadcrumb } from "./ItemBreadcrumb"

export function metric_options(reports, dataModel, current_subject_type, current_subject_uuid) {
    const subject_metrics = getSubjectTypeMetrics(current_subject_type, dataModel.subjects)
    let options = []
    reports.forEach((report) => {
        Object.entries(report.subjects).forEach(([subject_uuid, subject]) => {
            if (subject_uuid === current_subject_uuid) {
                return
            }
            const subject_name = getSubjectName(subject, dataModel)
            Object.entries(subject.metrics).forEach(([metric_uuid, metric]) => {
                if (!subject_metrics.includes(metric.type)) {
                    return
                }
                const metric_name = getMetricName(metric, dataModel)
                options.push({
                    content: <ItemBreadcrumb report={report.title} subject={subject_name} metric={metric_name} />,
                    key: metric_uuid,
                    text: report.title + subject_name + metric_name,
                    value: metric_uuid,
                })
            })
        })
    })
    options.sort((a, b) => a.text.localeCompare(b.text))
    return options
}

export function report_options(reports) {
    let options = []
    reports.forEach((report) => {
        options.push({ key: report.report_uuid, text: report.title, value: report.report_uuid })
    })
    options.sort((a, b) => a.text.localeCompare(b.text))
    return options
}

export function source_options(reports, dataModel, currentMetricType, currentMetricUuid) {
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
    options.sort((a, b) => a.text.localeCompare(b.text))
    return options
}

export function subject_options(reports, dataModel, current_report_uuid) {
    let options = []
    reports.forEach((report) => {
        if (report.report_uuid === current_report_uuid) {
            return
        }
        Object.entries(report.subjects).forEach(([subject_uuid, subject]) => {
            const subject_name = getSubjectName(subject, dataModel)
            options.push({
                content: <ItemBreadcrumb report={report.title} subject={subject_name} />,
                key: subject_uuid,
                text: report.title + subject_name,
                value: subject_uuid,
            })
        })
    })
    options.sort((a, b) => a.text.localeCompare(b.text))
    return options
}
