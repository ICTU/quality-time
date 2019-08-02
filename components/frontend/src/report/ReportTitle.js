import React, { useEffect, useState } from 'react';
import { Button, Grid, Icon, Segment, Table } from 'semantic-ui-react';
import TimeAgo from 'react-timeago';
import { StringInput } from '../fields/StringInput';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';
import { delete_report, set_report_attribute, get_changelog } from '../api/report';

function fetch_changelog(report_uuid, nrChanges, setChanges) {
    get_changelog(report_uuid, nrChanges)
        .then(function (json) {
            setChanges(json.changelog);
        })
}

function ChangeLog(props) {
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

export function ReportTitle(props) {
    return (
        <HeaderWithDetails level="h1" header={props.report.title} subheader={props.report.subtitle}>
            <Segment>
                <Grid stackable>
                    <Grid.Row columns={3}>
                        <Grid.Column>
                            <StringInput
                                label="Report title"
                                readOnly={props.readOnly}
                                set_value={(value) => set_report_attribute(props.report.report_uuid, "title", value, props.reload)}
                                value={props.report.title}
                            />
                        </Grid.Column>
                        <Grid.Column>
                            <StringInput
                                label="Report subtitle"
                                readOnly={props.readOnly}
                                set_value={(value) => set_report_attribute(props.report.report_uuid, "subtitle", value, props.reload)}
                                value={props.report.subtitle}
                            />
                        </Grid.Column>
                    </Grid.Row>
                    <Grid.Row>
                        <Grid.Column>
                            <ChangeLog report={props.report} />
                        </Grid.Column>
                    </Grid.Row>
                    {!props.readOnly &&
                        <Grid.Row>
                            <Grid.Column>
                                <Button
                                    basic
                                    floated='right'
                                    negative
                                    icon
                                    onClick={() => delete_report(props.report.report_uuid, props.go_home)}
                                    primary
                                >
                                    <Icon name='trash' /> Delete report
                                </Button>
                            </Grid.Column>
                        </Grid.Row>
                    }
                </Grid>
            </Segment>
        </HeaderWithDetails>
    )
}
