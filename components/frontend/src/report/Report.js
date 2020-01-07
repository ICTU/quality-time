import React, { useEffect, useState } from 'react';
import { Message } from 'semantic-ui-react';
import { Subjects } from '../subject/Subjects';
import { Tag } from '../widgets/Tag';
import { MetricSummaryCard } from '../dashboard/MetricSummaryCard';
import { CardDashboard } from '../dashboard/CardDashboard';
import { set_report_attribute } from '../api/report';
import { ReportTitle } from './ReportTitle';

function ReportDashboard(props) {
    const subject_cards = Object.entries(props.report.summary_by_subject).map(([subject_uuid, summary]) =>
        <MetricSummaryCard
            header={props.report.subjects[subject_uuid].name}
            key={subject_uuid}
            onClick={(event) => props.onClick(event, subject_uuid)}
            {...summary}
        />
    );
    const tag_cards = Object.entries(props.report.summary_by_tag).map(([tag, summary]) =>
        <MetricSummaryCard
            header={<Tag tag={tag} color={props.tags.includes(tag) ? "blue" : null} />}
            key={tag}
            onClick={() => props.setTags(tags => (tags.includes(tag) ? tags.filter((value) => value !== tag) : [tag, ...tags]))}
            {...summary}
        />
    );
    return (
        <CardDashboard
            cards={subject_cards.concat(tag_cards)}
            initial_layout={props.report.layout || []}
            save_layout={function(layout) {set_report_attribute(props.report.report_uuid, "layout", layout, props.reload)}}
        />
    )
}

export function Report(props) {
    function navigate_to_subject(event, subject_uuid) {
        event.preventDefault();
        document.getElementById(subject_uuid).scrollIntoView();
        window.scrollBy(0, -65);  // Correct for menu bar
    }
    const [tags, setTags] = useState([]);
    useEffect(() => {
        // Make sure we only filter by tags that are actually used in this report
        setTags(prev_tags => prev_tags.filter(tag => Object.keys(props.report.summary_by_tag || {}).includes(tag)))
    }, [props.report]);
    if (!props.report) {
        return (
            <Message warning size='huge'>
                <Message.Header>
                    {props.report_date ? `Sorry, this report didn't exist at ${props.report_date}` : "Sorry, this report doesn't exist"}
                </Message.Header>
            </Message>
        )
    }
    return (
        <>
            <ReportTitle
                go_home={props.go_home}
                report={props.report}
                reload={props.reload}
            />
            <ReportDashboard
                onClick={(e, s) => navigate_to_subject(e, s)}
                reload={props.reload}
                report={props.report}
                setTags={setTags}
                tags={tags}
            />
            <Subjects
                datamodel={props.datamodel}
                nr_measurements={props.nr_measurements}
                reload={props.reload}
                report={props.report}
                report_date={props.report_date}
                search_string={props.search_string}
                tags={tags}
                changed_fields={props.changed_fields}
            />
        </>
    )
}
