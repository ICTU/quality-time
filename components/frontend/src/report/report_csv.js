import { STATUS_NAME } from "../metric/status"
import { sortMetrics, subjectIsEmptyDueToFilters } from "../subject/Subject"
import { determineColumnsToHide } from "../subject/subject_column"
import { metricDelta, metricValueAndStatusOnDate } from "../subject/SubjectTableRow"
import {
    formatDays,
    formatMetricValueWithScale,
    getFormattedMetricTarget,
    getFormattedMetricTimeLeft,
    getFormattedMetricValue,
    getMetricComment,
    getMetricIssueIds,
    getMetricName,
    getMetricResponseOverrun,
    getMetricScale,
    getMetricStatus,
    getMetricTags,
    getMetricUnit,
    getSourceName,
    getSubjectName,
    identifyingParameterValues,
    visibleMetrics,
} from "../utils"
import { reverseSortMeasurements } from "./report_utils"

// The metric columns that can appear in the CSV, in the same order as the report table (the trend sparkline column is
// omitted because it has no textual representation). Date columns are inserted between "Metric" and "Status" for
// multi-date views, mirroring the table.
const COLUMNS = [
    { key: "status", label: "Status", value: (metric) => STATUS_NAME[getMetricStatus(metric)] },
    {
        key: "measurement",
        label: "Measurement",
        value: (metric, _uuid, { dataModel }) => getFormattedMetricValue(metric, dataModel),
    },
    {
        key: "target",
        label: "Target",
        // Mirror MeasurementTarget, but join the direction and value with a regular space instead of a non-breaking one
        value: (metric, _uuid, { dataModel }) => getFormattedMetricTarget(metric, dataModel, " "),
    },
    { key: "unit", label: "Unit", value: (metric, _uuid, { dataModel }) => getMetricUnit(metric, dataModel) },
    { key: "source", label: "Sources", value: sourcesValue },
    {
        key: "time_left",
        label: "Time left",
        value: (metric, _uuid, { report }) => getFormattedMetricTimeLeft(metric, report),
    },
    { key: "overrun", label: "Overrun", value: overrunValue },
    { key: "comment", label: "Comment", value: (metric) => htmlToText(getMetricComment(metric)) },
    { key: "issues", label: "Issues", value: (metric) => getMetricIssueIds(metric).join(", ") },
    { key: "tags", label: "Tags", value: (metric) => getMetricTags(metric).join(", ") },
]

function metricName(metric, dataModel) {
    // Mirror MetricName: the secondary name is shown on a second line below the metric name
    const name = getMetricName(metric, dataModel)
    return metric.secondary_name ? `${name}\n${metric.secondary_name}` : name
}

function sourcesValue(metric, _uuid, { dataModel }) {
    // Mirror SourceStatus: show the source name, followed by its identifying parameter values (such as the date of a
    // calendar source) on a second line, if any
    return Object.values(metric.sources ?? {})
        .map((source) => {
            const name = getSourceName(source, dataModel)
            const identifyingValues = identifyingParameterValues(source, dataModel.sources?.[source.type])
            return identifyingValues.length > 0 ? `${name}\n${identifyingValues.join(", ")}` : name
        })
        .join(", ")
}

function overrunValue(metric, metricUuid, { dataModel, report, measurements }) {
    // Mirror Overrun
    const { totalOverrun } = getMetricResponseOverrun(metricUuid, metric, report, measurements, dataModel)
    return totalOverrun === 0 ? "" : formatDays(totalOverrun)
}

function htmlToText(html) {
    // Convert the HTML comment to plain text so it fits in a single CSV cell. Links are kept by rewriting them as
    // "text (url)", or just the URL when the link text and the URL are equal, so the URL is not lost.
    if (!html) {
        return ""
    }
    const element = document.createElement("div")
    element.innerHTML = html
    element.querySelectorAll("a").forEach((anchor) => {
        const url = anchor.getAttribute("href")
        const text = anchor.textContent.trim()
        let replacement = text
        if (url) {
            replacement = text && text !== url ? `${text} (${url})` : url
        }
        anchor.replaceWith(replacement)
    })
    return element.textContent.replaceAll(/\s+/g, " ").trim()
}

function dateColumns(dates, showDelta) {
    // The date columns shown for a multi-date view, mirroring MeasurementHeaderCells: a delta (𝚫) column precedes each
    // value column except the first
    const columns = []
    dates.forEach((date, index) => {
        if (showDelta && index > 0) {
            columns.push({ delta: true, label: "𝚫" })
        }
        columns.push({ delta: false, label: date.toLocaleDateString() })
    })
    return columns
}

function dateCellValues(metric, metricUuid, csvContext, dates, showDelta) {
    // The measurement (and delta) values for a metric in a multi-date view, mirroring MeasurementCells
    const { dataModel, reversedMeasurements, dateOrderAscending } = csvContext
    const scale = getMetricScale(metric, dataModel)
    const values = []
    let previousValue = "?"
    dates.forEach((date, index) => {
        const [metricValue] = metricValueAndStatusOnDate(dataModel, metric, metricUuid, reversedMeasurements, date)
        if (showDelta && index > 0) {
            values.push(metricDelta(scale, metricValue, previousValue, dateOrderAscending))
        }
        values.push(formatMetricValueWithScale(metric, dataModel, metricValue))
        previousValue = metricValue === "?" ? previousValue : metricValue
    })
    return values
}

function visibleSubjectSections(report, measurements, nrDates, settings, dataModel) {
    // Return the subjects to export, in report order, with their filtered and sorted metrics and the columns hidden in
    // that subject, mirroring Subject.jsx and SubjectTable.jsx
    const sections = []
    Object.values(report.subjects ?? {}).forEach((subject) => {
        const metrics = visibleMetrics(subject.metrics, settings.metricsToHide.value, settings.hiddenTags.value)
        if (subjectIsEmptyDueToFilters(false, metrics, subject.metrics, settings)) {
            return
        }
        const metricEntries = Object.entries(metrics)
        if (settings.sortColumn.value !== "") {
            sortMetrics(
                dataModel,
                metricEntries,
                settings.sortDirection.value,
                settings.sortColumn.value,
                report,
                measurements,
            )
        }
        const columnsToHide = determineColumnsToHide(dataModel, measurements, metricEntries, nrDates, report, settings)
        sections.push({ subject, metricEntries, columnsToHide })
    })
    return sections
}

function columnVisible(key, sections) {
    // A column is included if it is visible in at least one of the exported subjects (mirroring the per-subject
    // "hide empty columns" behavior across the unified table)
    return sections.some((section) => !section.columnsToHide.includes(key))
}

function neutralizeFormula(value) {
    // Prevent CSV injection: a spreadsheet interprets a field starting with =, @, tab, or carriage return, or with + or
    // - when it is not a number, as a formula. Prefix such fields with a single quote so they are treated as text.
    const looksLikeFormula = /^[=@\t\r]/.test(value) || (/^[+-]/.test(value) && Number.isNaN(Number(value)))
    return looksLikeFormula ? `'${value}` : value
}

function csvField(value, delimiter) {
    // Escape a field according to RFC 4180: quote it if it contains the delimiter, a double quote, or a line break
    const field = neutralizeFormula(value)
    return field.includes(delimiter) || field.includes('"') || /[\r\n]/.test(field)
        ? `"${field.replaceAll('"', '""')}"`
        : field
}

export function listSeparator(locale) {
    // Excel opens a double-clicked CSV using the regional list separator. That separator is a semicolon in locales that
    // use a comma as decimal separator (such as Dutch and German) and a comma otherwise. Match it so the columns are
    // separated correctly, without resorting to a "sep=" line (which would make Excel ignore the UTF-8 byte order mark
    // and garble non-ASCII characters such as ≦ and ≧).
    return new Intl.NumberFormat(locale).format(1.1).charAt(1) === "," ? ";" : ","
}

export function reportToCSV(report, measurements, dates, settings, dataModel, delimiter = ",") {
    // Convert the report to a CSV string that mirrors the report table as currently displayed: the same subjects,
    // metrics (filtered, sorted), columns (hidden/empty), and date(s)
    const nrDates = dates.length
    const sections = visibleSubjectSections(report, measurements, nrDates, settings, dataModel)
    const showDates = nrDates > 1
    const showDelta = showDates && columnVisible("delta", sections)
    const dateCols = showDates ? dateColumns(dates, showDelta) : []
    const metricColumns = COLUMNS.filter((column) => columnVisible(column.key, sections))
    const csvContext = {
        dataModel: dataModel,
        report: report,
        measurements: measurements,
        reversedMeasurements: reverseSortMeasurements(measurements),
        dateOrderAscending: settings.dateOrder.value === "ascending",
    }
    const header = [
        "Subject",
        "Metric",
        ...dateCols.map((column) => column.label),
        ...metricColumns.map((c) => c.label),
    ]
    const rows = [header]
    sections.forEach((section) => {
        const subjectName = getSubjectName(section.subject, dataModel)
        section.metricEntries.forEach(([metricUuid, metric]) => {
            const row = [subjectName, metricName(metric, dataModel)]
            if (showDates) {
                row.push(...dateCellValues(metric, metricUuid, csvContext, dates, showDelta))
            }
            metricColumns.forEach((column) => row.push(column.value(metric, metricUuid, csvContext)))
            rows.push(row)
        })
    })
    return rows.map((row) => row.map((field) => csvField(field, delimiter)).join(delimiter)).join("\r\n")
}
