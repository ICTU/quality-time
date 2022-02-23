import React, { useEffect, useState } from 'react';
import { Icon } from 'semantic-ui-react';
import { Button, Feed, Form, Header, Segment } from '../semantic_ui_react_wrappers';
import { get_changelog } from '../api/changelog';
import { Avatar } from '../widgets/Avatar';
import { TimeAgoWithDate } from '../widgets/TimeAgoWithDate';
import './ChangeLog.css';

function Event({ description, email, timestamp }) {
    return (
        <Feed.Event>
            <Feed.Label><Avatar email={email} /></Feed.Label>
            <Feed.Content>
                <Feed.Summary>
                    {description}
                    <Feed.Date><TimeAgoWithDate date={timestamp} /></Feed.Date>
                </Feed.Summary>
            </Feed.Content>
        </Feed.Event>
    )
}

function ChangeLogWithoutMemo({ report_uuid, subject_uuid, metric_uuid, source_uuid, timestamp }) {
    const [changes, setChanges] = useState([]);
    const [nrChanges, setNrChanges] = useState(5);
    useEffect(() => {
        let didCancel = false;
        let uuids = {};
        if (report_uuid) { uuids.report_uuid = report_uuid }
        if (subject_uuid) { uuids.subject_uuid = subject_uuid }
        if (metric_uuid) { uuids.metric_uuid = metric_uuid }
        if (source_uuid) { uuids.source_uuid = source_uuid }
        get_changelog(nrChanges, uuids).then(function (json) {
            if (!didCancel) {
                setChanges(json.changelog || []);
            }
        });
        return () => { didCancel = true; };
    }, [report_uuid, subject_uuid, metric_uuid, source_uuid, timestamp, nrChanges]);

    let scope = "Changes in this instance of Quality-time";
    if (report_uuid) { scope = "Changes in this report" }
    if (subject_uuid) { scope = "Changes to this subject" }
    if (metric_uuid) { scope = "Changes to this metric and its sources" }
    if (source_uuid) { scope = "Changes to this source" }

    return (
        <Form>
            <Header size="small">
                {scope}
                <Header.Subheader>Most recent first</Header.Subheader>
            </Header>
            <Segment>
                <Feed size="small">
                    {changes.map(change =>
                        <Event key={change.timestamp + change.delta} description={change.delta} email={change.email} timestamp={change.timestamp} />)}
                </Feed>
                <Button basic icon primary size='small' onClick={() => setNrChanges(nrChanges + 10)}>
                    <Icon name="refresh" /> Load more changes
                </Button>
            </Segment>
        </Form>
    )
}

// Use React.memo so the ChangeLog is not re-rendered on reload, but only when one of its props change
export const ChangeLog = React.memo(props => <ChangeLogWithoutMemo {...props} />)
