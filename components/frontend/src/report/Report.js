import React, { useContext, useEffect, useState } from 'react';
import { Message } from 'semantic-ui-react';
import { Subjects } from '../subject/Subjects';
import { Tag } from '../widgets/Tag';
import { MetricSummaryCard } from '../dashboard/MetricSummaryCard';
import { CardDashboard } from '../dashboard/CardDashboard';
import { DataModel } from '../context/DataModel';
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from '../context/Permissions';
import { set_report_attribute } from '../api/report';
import { get_subject_name, useURLSearchQuery } from '../utils';
import { ReportTitle } from './ReportTitle';
import { DataModel } from '../context/Contexts';

function ReportDashboard({report, onClick, hideTags, setTags, tags, reload}) {
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
        return hideTags ? [] : Object.entries(report.summary_by_tag).map(([tag, summary]) =>
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
        history}) {
    function navigate_to_subject(event, subject_uuid) {
        event.preventDefault();
        document.getElementById(subject_uuid).scrollIntoView();
        window.scrollBy(0, -65);  // Correct for menu bar
    }

    const [tags, setTags] = useState([]);
    useEffect(() => {
        // Make sure we only filter by tags that are actually used in this report
        setTags(prev_tags => prev_tags.filter(tag => Object.keys(report.summary_by_tag || {}).includes(tag)))
    }, [report]);

    // eslint-disable-next-line
    const [hiddenColumns, toggleHiddenColumn] = useURLSearchQuery(history, "hidden_columns", "array");

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
            <ReportDashboard
                onClick={(e, s) => navigate_to_subject(e, s)}
                hideTags={hiddenColumns.includes("tags")}
                setTags={setTags}
                tags={tags}
                report={report}
                reload={reload}
            />
            <Subjects
                hiddenColumns={hiddenColumns}
                tags={tags}
                toggleHiddenColumn={toggleHiddenColumn}
                report={report}
                report_date={report_date}
                changed_fields={changed_fields}
                reload={reload}
                reports={reports}
                history={history}
            />
        </div>
    )
}
