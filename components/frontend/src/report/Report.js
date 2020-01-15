import React, { useEffect, useState } from 'react';
import { Message } from 'semantic-ui-react';
import { Subjects } from '../subject/Subjects';
import { Tag } from '../widgets/Tag';
import { MetricSummaryCard } from '../dashboard/MetricSummaryCard';
import { CardDashboard } from '../dashboard/CardDashboard';
import { set_report_attribute } from '../api/report';
import { get_subject_name } from '../utils';
import { ReportTitle } from './ReportTitle';

function ReportDashboard(props) {
    const subject_cards = Object.entries(props.report.summary_by_subject).map(([subject_uuid, summary]) =>
        <MetricSummaryCard
            header={get_subject_name(props.report.subjects[subject_uuid], props.datamodel)}
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
            save_layout={function (layout) { set_report_attribute(props.report.report_uuid, "layout", layout, props.reload) }}
        />
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
        return <ReportErrorMessage report_date={props.report_date} />
    }
    return (
        <>
            <ReportTitle {...props} />
            <ReportDashboard
                onClick={(e, s) => navigate_to_subject(e, s)}
                setTags={setTags}
                tags={tags}
                {...props}
            />
            <Subjects tags={tags} {...props} />
        </>
    )
}
