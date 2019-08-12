import React, { useEffect, useState } from 'react';
import { Button, Icon, Table } from 'semantic-ui-react';
import TimeAgo from 'react-timeago';
import { get_changelog } from '../api/report';


function fetch_changelog(uuids, nrChanges, setChanges) {
    get_changelog(nrChanges, uuids)
        .then(function (json) {
            setChanges(json.changelog);
        })
}

export function ChangeLog(props) {
    let scope = "All changes in this report";
    if (props.subject_uuid) {
        scope = "All changes to this subject";
    }
    if (props.metric_uuid) {
        scope = "All changes to this metric and its sources";
    }
    if (props.source_uuid) {
        scope = "All changes to this source";
    }
    const [nrChanges, setNrChanges] = useState(10);
    const [changes, setChanges] = useState([]);
    useEffect(() => {
        let uuids = { report_uuid: props.report.report_uuid };
        if (props.subject_uuid) {
            uuids.subject_uuid = props.subject_uuid;
        }
        if (props.metric_uuid) {
            uuids.metric_uuid = props.metric_uuid;
        }
        if (props.source_uuid) {
            uuids.source_uuid = props.source_uuid;
        }
        fetch_changelog(uuids, nrChanges, setChanges)
    }, [props.report.report_uuid, props.subject_uuid, props.metric_uuid, props.source_uuid, props.report.timestamp, nrChanges]);
    let rows = [];
    changes.forEach((change) => rows.push(<Table.Row key={change.timestamp + change.delta}>
        <Table.Cell>
            <TimeAgo date={change.timestamp} />, {(new Date(change.timestamp)).toLocaleString()}, <span dangerouslySetInnerHTML={{__html: change.delta}}/>
        </Table.Cell>
    </Table.Row>))
    return (
        <Table striped size='small'>
            <Table.Header>
                <Table.Row>
                    <Table.HeaderCell>
                        {scope} (most recent first)
                    </Table.HeaderCell>
                </Table.Row>
            </Table.Header>
            <Table.Body>
                {rows}
            </Table.Body>
            <Table.Footer>
                <Table.Row>
                    <Table.HeaderCell>
                        <Button basic icon primary size='small' onClick={() => setNrChanges(nrChanges+10)}>
                            <Icon name="refresh" /> Load more changes
                        </Button>
                    </Table.HeaderCell>
                </Table.Row>
            </Table.Footer>
        </Table>
    )
}