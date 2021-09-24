import React, { useEffect, useState } from 'react';
import { Button, Feed, Form, Icon, Segment } from 'semantic-ui-react';
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
                    <Feed.Date><TimeAgoWithDate date={timestamp}/></Feed.Date>
                </Feed.Summary>
            </Feed.Content>
        </Feed.Event>
    )
}

function ChangeLogWithoutMemo(props) {
    const [changes, setChanges] = useState([]);
    const [nrChanges, setNrChanges] = useState(5);
    useEffect(() => {
        let didCancel = false;
        let uuids = {};
        if (props.report_uuid) { uuids.report_uuid = props.report_uuid }
        if (props.subject_uuid) { uuids.subject_uuid = props.subject_uuid }
        if (props.metric_uuid) { uuids.metric_uuid = props.metric_uuid }
        if (props.source_uuid) { uuids.source_uuid = props.source_uuid }
        get_changelog(nrChanges, uuids).then(function (json) {
            if (!didCancel) {
                setChanges(json.changelog || []);
            }
        });
        return () => { didCancel = true; };
    }, [props.report_uuid, props.subject_uuid, props.metric_uuid, props.source_uuid, props.timestamp, nrChanges]);

    let scope = "Changes in this instance of Quality-time";
    if (props.report_uuid) { scope = "Changes in this report" }
    if (props.subject_uuid) { scope = "Changes to this subject" }
    if (props.metric_uuid) { scope = "Changes to this metric and its sources" }
    if (props.source_uuid) { scope = "Changes to this source" }

    return (
        <Form>
            <div className="field" style={{ marginBottom: "0pt" }}>
                <label>
                    {scope} (most recent first)
                </label>
            </div>
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
