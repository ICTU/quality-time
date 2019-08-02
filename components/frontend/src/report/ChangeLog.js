import React, { useEffect, useState } from 'react';
import { Button, Icon, Table } from 'semantic-ui-react';
import TimeAgo from 'react-timeago';
import { get_changelog } from '../api/report';


function fetch_changelog(report_uuid, nrChanges, setChanges) {
    get_changelog(report_uuid, nrChanges)
        .then(function (json) {
            setChanges(json.changelog);
        })
}

export function ChangeLog(props) {
    const [nrChanges, setNrChanges] = useState(10);
    const [changes, setChanges] = useState([]);
    useEffect(() => {
        fetch_changelog(props.report.report_uuid, nrChanges, setChanges)
        // eslint-disable-next-line
    }, [props.report.report_uuid, props.report.timestamp, nrChanges]);
    let rows = [];
    changes.forEach((change) => rows.push(<Table.Row key={change.timestamp + change.delta}>
        <Table.Cell>
            <TimeAgo date={change.timestamp} />, {(new Date(change.timestamp)).toLocaleString()}, {change.delta}
        </Table.Cell>
    </Table.Row>))
    return (
        <Table striped size='small'>
            <Table.Header>
                <Table.Row>
                    <Table.HeaderCell>
                        Changes (most recent first)
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