import React, { useEffect, useState } from 'react';
import { Button, Feed, Form, Icon, Segment } from 'semantic-ui-react';
import TimeAgo from 'react-timeago';
import { get_changelog } from '../api/changelog';
import { Avatar } from '../widgets/Avatar';
import './ChangeLog.css';

export function ChangeLog(props) {
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

    let events = [];
    changes.forEach((change) => events.push(
        <Feed.Event key={change.timestamp + change.delta}>
            <Feed.Label>
                <Avatar email={change.email} />
            </Feed.Label>
            <Feed.Content>
                <Feed.Summary>
                    <span dangerouslySetInnerHTML={{ __html: change.delta }} />
                    <Feed.Date>
                        {(new Date(change.timestamp)).toLocaleString()}, <TimeAgo date={change.timestamp} />
                    </Feed.Date>
                </Feed.Summary>
            </Feed.Content>
        </Feed.Event>));

    return (
        <Form>
            <div className="field" style={{marginBottom: "0pt"}}>
                <label>
                    {scope} (most recent first)
                </label>
            </div>
            <Segment>
                <Feed size="small">
                    {events}
                </Feed>
                <Button basic icon primary size='small' onClick={() => setNrChanges(nrChanges + 10)}>
                    <Icon name="refresh" /> Load more changes
                </Button>
            </Segment>
        </Form>
    )
}