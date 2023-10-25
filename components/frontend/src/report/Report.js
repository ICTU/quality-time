import React, { useContext } from 'react';
import PropTypes from 'prop-types';
import {
    datesPropType,
    optionalDatePropType,
    reportPropType,
    reportsPropType,
    settingsPropType,
    stringsPropType,
    stringsURLSearchQueryPropType
} from '../sharedPropTypes';
import { DataModel } from '../context/DataModel';
import { Subjects } from '../subject/Subjects';
import { SubjectsButtonRow } from '../subject/SubjectsButtonRow';
import { CommentSegment } from '../widgets/CommentSegment';
import { Tag } from '../widgets/Tag';
import { CardDashboard } from '../dashboard/CardDashboard';
import { LegendCard } from '../dashboard/LegendCard';
import { MetricSummaryCard } from '../dashboard/MetricSummaryCard';
import { set_report_attribute } from '../api/report';
import { getReportTags, getMetricTags, nrMetricsInReport, get_subject_name, STATUS_COLORS, visibleMetrics } from '../utils';
import { ReportErrorMessage } from './ReportErrorMessage';
import { ReportTitle } from './ReportTitle';
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

function ReportDashboard(
    {
        dates,
        hiddenTags,
        measurements,
        onClick,
        onClickTag,
        reload,
        report
    }
) {
    const dataModel = useContext(DataModel)
    const nrMetrics = Math.max(nrMetricsInReport(report), 1);
    const subjectCards = []
    Object.entries(report.subjects).forEach(([subject_uuid, subject]) => {
        const metrics = visibleMetrics(subject.metrics, "none", hiddenTags.value)
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
    const anyTagsHidden = hiddenTags.value.length > 0
    const tagCards = getReportTags(report, hiddenTags.value).map((tag) => {
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
    hiddenTags: stringsURLSearchQueryPropType,
    measurements: PropTypes.array,
    onClick: PropTypes.func,
    onClickTag: PropTypes.func,
    reload: PropTypes.func,
    report: reportPropType
}

export function Report({
    changed_fields,
    dates,
    handleSort,
    measurements,
    openReportsOverview,
    reload,
    report,
    report_date,
    reports,
    settings
}) {
    function navigate_to_subject(event, subject_uuid) {
        event.preventDefault();
        document.getElementById(subject_uuid).scrollIntoView();
        window.scrollBy(0, 163);  // Correct for menubar and subject title margin
    }

    if (!report) {
        return <ReportErrorMessage reportDate={report_date} />
    }
    // Sort measurements in reverse order so that if there multiple measurements on a day, we find the most recent one:
    const reversedMeasurements = measurements.slice().sort((m1, m2) => m1.start < m2.start ? 1 : -1)
    return (
        <div id="dashboard">
            <ReportTitle
                openReportsOverview={openReportsOverview}
                report={report}
                changed_fields={changed_fields}
                reload={reload}
                report_date={report_date}
                reports={reports}
            />
            <CommentSegment comment={report.comment} />
            <ReportDashboard
                dates={dates}
                hiddenTags={settings.hiddenTags}
                measurements={reversedMeasurements}
                onClick={(e, s) => navigate_to_subject(e, s)}
                onClickTag={(tag) => {
                    // If there are hidden tags (hiddenTags.length > 0), show the hidden tags.
                    // Otherwise, hide all tags in this report except the one clicked on.
                    const tagsToToggle = settings.hiddenTags.value.length > 0 ? settings.hiddenTags.value : getReportTags(report)
                    settings.hiddenTags.toggle(...tagsToToggle.filter((visibleTag) => visibleTag !== tag))
                }}
                report={report}
                reload={reload}
            />
            <Subjects
                atReportsOverview={false}
                changed_fields={changed_fields}
                dates={dates}
                handleSort={handleSort}
                measurements={measurements}
                reload={reload}
                reports={reports}
                reportsToShow={[report]}
                report_date={report_date}
                settings={settings}
            />
            <SubjectsButtonRow reload={reload} report={report} reports={reports} />
        </div>
    )
}
Report.propTypes = {
    changed_fields: stringsPropType,
    dates: datesPropType,
    handleSort: PropTypes.func,
    measurements: PropTypes.array,
    openReportsOverview: PropTypes.func,
    reload: PropTypes.func,
    report: reportPropType,
    report_date: optionalDatePropType,
    reports: reportsPropType,
    settings: settingsPropType
}
