import React, { useContext, useEffect, useState } from 'react';
import { Message } from 'semantic-ui-react';
import { Subjects } from '../subject/Subjects';
import { CommentSegment } from '../widgets/CommentSegment';
import { HamburgerMenu } from '../widgets/HamburgerMenu';
import { Tag } from '../widgets/Tag';
import { MetricSummaryCard } from '../dashboard/MetricSummaryCard';
import { CardDashboard } from '../dashboard/CardDashboard';
import { DataModel } from '../context/DataModel';
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { set_report_attribute } from '../api/report';
import { get_subject_name, useURLSearchQuery } from '../utils';
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
                header={<Tag tag={tag} color={tags.includes(tag) ? "blue" : null} />}
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
    go_home,
    nr_measurements,
    report,
    changed_fields,
    reload,
    report_date,
    reports,
    history }) {

    function navigate_to_subject(event, subject_uuid) {
        event.preventDefault();
        document.getElementById(subject_uuid).scrollIntoView();
        window.scrollBy(0, 55);  // Correct for menubar and subject title margin
    }

    const [tags, setTags] = useState([]);
    useEffect(() => {
        // Make sure we only filter by tags that are actually used in this report
        setTags(prev_tags => prev_tags.filter(tag => Object.keys(report.summary_by_tag || {}).includes(tag)))
    }, [report]);

    const [hiddenColumns, toggleHiddenColumn] = useURLSearchQuery(history, "hidden_columns", "array");
    const [sortColumn, setSortColumn] = useURLSearchQuery(history, "sort_column", "string", null)
    const [sortDirection, setSortDirection] = useURLSearchQuery(history, "sort_direction", "string", "ascending")
    const [hideMetricsNotRequiringAction, setHideMetricsNotRequiringAction] = useURLSearchQuery(history, "hide_metrics_not_requiring_action", "boolean", false);
    const [visibleDetailsTabs, toggleVisibleDetailsTab, clearVisibleDetailsTabs] = useURLSearchQuery(history, "tabs", "array");
    const [nrDates, setNrDates] = useURLSearchQuery(history, "nr_dates", "integer", 1);
    const [dateInterval, setDateInterval] = useURLSearchQuery(history, "date_interval", "integer", 7);

    function handleSort(column) {
        if (column === null) {
            setSortColumn(null)  // Stop sorting
            return
        }
        if (sortColumn === column) {
            if (sortDirection === 'descending') {
                setSortColumn(null)  // Cycle through ascending->descending->no sort as long as the user clicks the same column
            }
            setSortDirection(sortDirection === 'ascending' ? 'descending' : 'ascending')
        } else {
            setSortColumn(column)
        }
    }

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
                hamburgerMenu={
                    <HamburgerMenu
                        clearVisibleDetailsTabs={clearVisibleDetailsTabs}
                        dateInterval={dateInterval}
                        hiddenColumns={hiddenColumns}
                        hideMetricsNotRequiringAction={hideMetricsNotRequiringAction}
                        nrDates={nrDates}
                        setDateInterval={(interval) => setDateInterval(interval)}
                        setHideMetricsNotRequiringAction={(state) => setHideMetricsNotRequiringAction(state)}
                        setNrDates={(nr) => setNrDates(nr)}
                        toggleHiddenColumn={toggleHiddenColumn}
                        visibleDetailsTabs={visibleDetailsTabs}
                    />
                }
                handleSort={(column) => handleSort(column)}
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
