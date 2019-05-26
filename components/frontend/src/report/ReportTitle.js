import React from 'react';
import { Button, Grid, Icon, Segment } from 'semantic-ui-react';
import { StringInput } from '../fields/StringInput';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';

export function ReportTitle(props) {
    return (
        <HeaderWithDetails level="h2" header={props.report.title} subheader={props.report.subtitle}>
            <Segment>
                <Grid stackable>
                    <Grid.Row columns={3}>
                        <Grid.Column>
                            <StringInput
                                label="Report title"
                                readOnly={props.readOnly}
                                set_value={(value) => props.set_report_attribute("title", value)}
                                value={props.report.title}
                            />
                        </Grid.Column>
                        <Grid.Column>
                            <StringInput
                                label="Report subtitle"
                                readOnly={props.readOnly}
                                set_value={(value) => props.set_report_attribute("subtitle", value)}
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
                                    onClick={(e) => props.delete_report(e)}
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
