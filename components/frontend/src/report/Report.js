import React from 'react';
import { Subjects } from '../subject/Subjects';
import { Tag } from '../widgets/Tag';
import { MetricSummaryCard } from '../dashboard/MetricSummaryCard';
import { CardDashboard } from '../dashboard/CardDashboard';
import { ReportTitle } from './ReportTitle'

function ReportDashboard(props) {
    const subject_cards = Object.entries(props.report.summary_by_subject).map(([subject_uuid, summary]) =>
        <MetricSummaryCard
            key={subject_uuid} header={props.report.subjects[subject_uuid].name}
            onClick={(event) => props.onClick(event, subject_uuid)} {...summary} />);
    const tag_cards = Object.entries(props.report.summary_by_tag).map(([tag, summary]) =>
        <MetricSummaryCard key={tag} header={<Tag tag={tag} />} {...summary} />);
    return (
        <CardDashboard big_cards={subject_cards} small_cards={tag_cards} />
    )
}

export function Report(props) {
    function navigate_to_subject(event, subject_uuid) {
        event.preventDefault();
        document.getElementById(subject_uuid).scrollIntoView();
        window.scrollBy(0, -65);  // Correct for menu bar
    }
    return (
        <>
            <ReportTitle
                go_home={props.go_home}
                report={props.report}
                readOnly={props.readOnly}
                reload={props.reload}
            />
            <ReportDashboard report={props.report} onClick={(e, s) => navigate_to_subject(e, s)} />
            <Subjects
                datamodel={props.datamodel}
                nr_new_measurements={props.nr_new_measurements}
                readOnly={props.readOnly}
                reload={props.reload}
                report={props.report}
                report_date={props.report_date}
                search_string={props.search_string}
            />
        </>
    )
}
