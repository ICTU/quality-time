import React from 'react';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';
import { Grid } from 'semantic-ui-react';
import { ChangeLog } from '../changelog/ChangeLog';
import { StringInput } from '../fields/StringInput';
import { MultipleChoiceInput } from '../fields/MultipleChoiceInput';
import { set_reports_attribute } from '../api/report';

export function ReportsTitle(props) {
    return (
        <HeaderWithDetails level="h1" header={props.title} subheader={props.subtitle}>
            <Grid stackable>
                <Grid.Row columns={2}>
                    <Grid.Column>
                        <StringInput
                            label="Report overview title"
                            set_value={(value) => set_reports_attribute("title", value, props.reload)}
                            value={props.title}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <StringInput
                            label="Report overview subtitle"
                            set_value={(value) => set_reports_attribute("subtitle", value, props.reload)}
                            value={props.subtitle}
                        />
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row columns={1}>
                    <Grid.Column>
                        <MultipleChoiceInput
                            allowAdditions
                            label="Users allowed to edit reports (user name or email address)"
                            options={props.editors}
                            placeholder="All authenticated users"
                            set_value={(value) => set_reports_attribute("editors", value, props.reload)}
                            value={props.editors}
                        />
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row>
                    <Grid.Column>
                        <ChangeLog />
                    </Grid.Column>
                </Grid.Row>
            </Grid>
        </HeaderWithDetails>
    )
}
