import React from 'react';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';
import { Grid, Segment } from 'semantic-ui-react';
import { ChangeLog } from '../changelog/ChangeLog';
import { StringInput } from '../fields/StringInput';
import { set_reports_attribute } from '../api/report';

export function ReportsTitle(props) {
    return (
        <HeaderWithDetails level="h1" header={props.title} subheader={props.subtitle}>
            <Segment>
                <Grid stackable>
                    <Grid.Row columns={3}>
                        <Grid.Column>
                            <StringInput
                                label="Report overview title"
                                readOnly={props.readOnly}
                                set_value={(value) => set_reports_attribute("title", value, props.reload)}
                                value={props.title}
                            />
                        </Grid.Column>
                        <Grid.Column>
                            <StringInput
                                label="Report overview subtitle"
                                readOnly={props.readOnly}
                                set_value={(value) => set_reports_attribute("subtitle", value, props.reload)}
                                value={props.subtitle}
                            />
                        </Grid.Column>
                    </Grid.Row>
                    <Grid.Row>
                        <Grid.Column>
                            <ChangeLog />
                        </Grid.Column>
                    </Grid.Row>
                </Grid>
            </Segment>
        </HeaderWithDetails>
    )
}
