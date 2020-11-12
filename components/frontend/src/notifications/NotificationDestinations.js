import React from 'react';
import { Grid, Icon, Segment } from 'semantic-ui-react';
import { StringInput } from '../fields/StringInput';
import { AddButton, DeleteButton } from '../widgets/Button';
import { add_notification_destination, delete_notification_destination, set_notification_destination_attributes } from '../api/notification'
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { HyperLink } from '../widgets/HyperLink';

function NotificationDestination({report_uuid, destination_uuid, destination, reload}){
    const help_url = "https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook";
    const label = <label>Microsoft Teams webhook <HyperLink url={help_url}><Icon name="help circle" link /></HyperLink></label>;
    return (
        <Segment vertical key={destination_uuid}>
            <Grid stackable>
                <Grid.Row columns={2}>
                    <Grid.Column width={4}>
                        <StringInput
                            id={destination_uuid}
                            label='Name'
                            set_value={(value) => {
                                set_notification_destination_attributes(report_uuid, destination_uuid, {name: value}, reload)
                            }}
                            value={destination.name}
                        />
                    </Grid.Column>
                    <Grid.Column width={12}>
                        <StringInput
                            placeholder="url"
                            label={label}
                            set_value={(value) => {
                                set_notification_destination_attributes(report_uuid, destination_uuid, {teams_webhook: value, url: window.location.href}, reload)
                            }}
                            value={destination.teams_webhook}
                        />
                    </Grid.Column>
                </Grid.Row>
                <ReadOnlyOrEditable editableComponent={
                    <Grid.Row>
                        <Grid.Column>
                            <DeleteButton
                                item_type='notification destination'
                                onClick={() => delete_notification_destination(report_uuid, destination_uuid, reload)}
                            />
                        </Grid.Column>
                    </Grid.Row>}
                />
            </Grid>
        </Segment>
    )
}

export function NotificationDestinations({destinations, report_uuid, reload}) {
    const result = [];
    if(destinations){
        Object.entries(destinations).forEach(([destination_uuid, destination]) => {
            result.push(
                <NotificationDestination key={destination_uuid} report_uuid={report_uuid} destination_uuid={destination_uuid} destination={destination} reload={reload}/>
            )
        })
    }
    result.push(
        <ReadOnlyOrEditable key="1" editableComponent={
            <Segment vertical>
                <AddButton
                    item_type="notification destination"
                    report_uuid={report_uuid}
                    onClick={() => add_notification_destination(report_uuid, reload)}
                />
            </Segment>}
        />
    )
    return (
        <Grid.Row>
            <Grid.Column>
                {result}
            </Grid.Column>
        </Grid.Row>
    )
}
