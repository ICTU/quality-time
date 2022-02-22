import React, { useContext, useEffect, useState } from 'react';
import { Message } from 'semantic-ui-react';
import { Subjects } from '../subject/Subjects';
import { CommentSegment } from '../widgets/CommentSegment';
import { Tag } from '../widgets/Tag';
import { MetricSummaryCard } from '../dashboard/MetricSummaryCard';
import { CardDashboard } from '../dashboard/CardDashboard';
import { DataModel } from '../context/DataModel';
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { set_report_attribute } from '../api/report';
import { get_subject_name } from '../utils';
import { ReportTitle } from './ReportTitle';

function ReportDashboard({ report, onClick, setTags, tags, reload }) {
    const dataModel = useContext(DataModel)
    function subject_cards() {
        return Object.entries(report.summary_by_subject).map(([subject_uuid, summary]) =>
            <MetricSummaryCard
                header={get_subject_name(report.subjects[subject_uuid], dataModel)}
                key={subject_uuid}
                onClick={(event) => onClick(event, subject_uuid)}
                {...summary}
            />
        );
    }
    function tag_cards() {
        return Object.entries(report.summary_by_tag).map(([tag, summary]) =>
            <MetricSummaryCard
                header={<Tag tag={tag} selected={tags.includes(tag)} />}
                key={tag}
                onClick={() => setTags(tag_list => (tag_list.includes(tag) ? tag_list.filter((value) => value !== tag) : [tag, ...tag_list]))}
                {...summary}
            />
        );
    }
    return (
        <Permissions.Consumer>{(permissions) => (
            <CardDashboard
                cards={subject_cards().concat(tag_cards())}
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
    dateInterval,
    dateOrder,
    go_home,
    handleSort,
    hiddenColumns,
    hideMetricsNotRequiringAction,
    history,
    nrDates,
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

    const [tags, setTags] = useState([]);
    useEffect(() => {
        // Make sure we only filter by tags that are actually used in this report
        setTags(prev_tags => prev_tags.filter(tag => Object.keys(report.summary_by_tag || {}).includes(tag)))
    }, [report]);

    if (!report) {
        return <ReportErrorMessage report_date={report_date} />
    }
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
                onClick={(e, s) => navigate_to_subject(e, s)}
                setTags={setTags}
                tags={tags}
                report={report}
                reload={reload}
            />
            <Subjects
                changed_fields={changed_fields}
                dateInterval={dateInterval}
                dateOrder={dateOrder}
                handleSort={handleSort}
                hiddenColumns={hiddenColumns}
                hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
                nrDates={nrDates}
                reload={reload}
                report={report}
                reports={reports}
                report_date={report_date}
                sortColumn={sortColumn}
                sortDirection={sortDirection}
                tags={tags}
                toggleVisibleDetailsTab={toggleVisibleDetailsTab}
                visibleDetailsTabs={visibleDetailsTabs}
            />
        </div>
    )
}
