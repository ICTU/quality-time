import React, { useContext, useEffect, useState } from 'react';
import { Message } from 'semantic-ui-react';
import { DataModel } from '../context/DataModel';
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { Subjects } from '../subject/Subjects';
import { CommentSegment } from '../widgets/CommentSegment';
import { Tag } from '../widgets/Tag';
import { CardDashboard } from '../dashboard/CardDashboard';
import { LegendCard } from '../dashboard/LegendCard';
import { MetricSummaryCard } from '../dashboard/MetricSummaryCard';
import { get_report_measurements, set_report_attribute } from '../api/report';
import { getReportTags, getMetricTags, get_subject_name, STATUS_COLORS } from '../utils';
import { ReportTitle } from './ReportTitle';


function ReportDashboard({ dates, measurements, report, onClick, setSelectedTags, selectedTags, reload }) {
    const dataModel = useContext(DataModel)
    function subject_cards() {
        const summary = {}
        Object.entries(report.subjects).forEach(([subject_uuid, subject]) => {
            summary[subject_uuid] = {}
            dates.forEach((date) => {
                const iso_date_string = date.toISOString().split("T")[0];
                summary[subject_uuid][date] = { red: 0, yellow: 0, green: 0, blue: 0, grey: 0, white: 0 }
                Object.entries(subject.metrics).forEach(([metric_uuid, metric]) => {
                    const measurement = measurements?.find((m) => { return m.metric_uuid === metric_uuid && m.start.split("T")[0] <= iso_date_string && iso_date_string <= m.end.split("T")[0] })
                    const status = measurement?.[metric.scale]?.status ?? "unknown";
                    summary[subject_uuid][date][STATUS_COLORS[status]] += 1
                })
            })
        })
        return Object.keys(report.subjects).map((subject_uuid) =>
            <MetricSummaryCard
                header={get_subject_name(report.subjects[subject_uuid], dataModel)}
                key={subject_uuid}
                onClick={(event) => onClick(event, subject_uuid)}
                summary={summary[subject_uuid]}
            />
        );
    }
    function tag_cards() {
        const summary = {}
        const tags = getReportTags(report)
        tags.forEach((tag) => {
            summary[tag] = {}
            dates.forEach((date) => {
                const iso_date_string = date.toISOString().split("T")[0];
                summary[tag][date] = { red: 0, yellow: 0, green: 0, blue: 0, grey: 0, white: 0 }
                Object.values(report.subjects).forEach(subject => {
                    Object.entries(subject.metrics).forEach(([metric_uuid, metric]) => {
                        if (getMetricTags(metric).indexOf(tag) >= 0) {
                            const measurement = measurements?.find((m) => { return m.metric_uuid === metric_uuid && m.start.split("T")[0] <= iso_date_string && iso_date_string <= m.end.split("T")[0] })
                            const status = measurement?.[metric.scale]?.status ?? "unknown";
                            summary[tag][date][STATUS_COLORS[status]] += 1
                        }
                    })
                })
            })
        })
        return tags.map((tag) =>
            <MetricSummaryCard
                header={<Tag tag={tag} selected={selectedTags.includes(tag)} />}
                key={tag}
                onClick={() => setSelectedTags(tag_list => (tag_list.includes(tag) ? tag_list.filter((value) => value !== tag) : [tag, ...tag_list]))}
                summary={summary[tag]}
            />
        );
    }
    return (
        <Permissions.Consumer>{(permissions) => (
            <CardDashboard
                cards={subject_cards().concat(tag_cards().concat([<LegendCard key="legend" />]))}
                initial_layout={report.layout || []}
                save_layout={function (layout) { if (accessGranted(permissions, [EDIT_REPORT_PERMISSION])) { set_report_attribute(report.report_uuid, "layout", layout, reload) } }}
            />)}
        </Permissions.Consumer>
    )
}

function ReportErrorMessage({ report_date }) {
    return (
        <Message warning size='huge'>
            <Message.Header>
                {report_date ? `Sorry, this report didn't exist at ${report_date}` : "Sorry, this report doesn't exist"}
            </Message.Header>
        </Message>
    )
}

export function Report({
    changed_fields,
    dates,
    go_home,
    handleSort,
    hiddenColumns,
    hideMetricsNotRequiringAction,
    history,
    issueSettings,
    nr_measurements,
    reload,
    report,
    report_date,
    reports,
    sortColumn,
    sortDirection,
    toggleVisibleDetailsTab,
    visibleDetailsTabs
}) {

    function navigate_to_subject(event, subject_uuid) {
        event.preventDefault();
        document.getElementById(subject_uuid).scrollIntoView();
        window.scrollBy(0, 163);  // Correct for menubar and subject title margin
    }

    const [measurements, setMeasurements] = useState([]);
    useEffect(() => {
        if (report) {
            const minReportDate = dates.slice().sort((d1, d2) => { return d1.getTime() - d2.getTime() }).at(0);
            get_report_measurements(report.report_uuid, report_date, minReportDate).then(json => {
                setMeasurements(json.measurements ?? [])
            })
        }
        // eslint-disable-next-line
    }, [dates, report_date]);

    const [selectedTags, setSelectedTags] = useState([]);
    useEffect(() => {
        // Make sure we only filter by tags that are actually used in this report
        setSelectedTags(prev_tags => prev_tags.filter(tag => getReportTags(report).includes(tag)))
    }, [report]);

    if (!report) {
        return <ReportErrorMessage report_date={report_date} />
    }
    // Sort measurements in reverse order so that if there multiple measurements on a day, we find the most recent one:
    const reversedMeasurements = measurements.slice().sort((m1, m2) => m1.start < m2.start ? 1 : -1)
    return (
        <div id="dashboard">
            <ReportTitle
                go_home={go_home}
                nr_measurements={nr_measurements}
                report={report}
                changed_fields={changed_fields}
                reload={reload}
                report_date={report_date}
                reports={reports}
                history={history} />
            <CommentSegment comment={report.comment} />
            <ReportDashboard
                dates={dates}
                measurements={reversedMeasurements}
                onClick={(e, s) => navigate_to_subject(e, s)}
                setSelectedTags={setSelectedTags}
                selectedTags={selectedTags}
                report={report}
                reload={reload}
            />
            <Subjects
                changed_fields={changed_fields}
                dates={dates}
                handleSort={handleSort}
                hiddenColumns={hiddenColumns}
                hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
                issueSettings={issueSettings}
                measurements={measurements}
                reload={reload}
                report={report}
                reports={reports}
                report_date={report_date}
                sortColumn={sortColumn}
                sortDirection={sortDirection}
                tags={selectedTags}
                toggleVisibleDetailsTab={toggleVisibleDetailsTab}
                visibleDetailsTabs={visibleDetailsTabs}
            />
        </div>
    )
}
