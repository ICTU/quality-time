import React from 'react';
import { Button, Grid, Icon, Segment } from 'semantic-ui-react';
import { StringInput } from '../fields/StringInput';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';
import { delete_report, set_report_attribute } from '../api/report';

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
