import { func, objectOf, string } from "prop-types"
import { Grid, Message } from "semantic-ui-react"
import { Segment } from "../semantic_ui_react_wrappers"
import { StringInput } from "../fields/StringInput"
import { AddButton, DeleteButton } from "../widgets/Button"
import { LabelWithHelp } from "../widgets/LabelWithHelp"
import {
    add_notification_destination,
    delete_notification_destination,
    set_notification_destination_attributes,
} from "../api/notification"
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from "../context/Permissions"
import { HyperLink } from "../widgets/HyperLink"
import { destinationPropType } from "../sharedPropTypes"

function NotificationDestination({ destination, destination_uuid, reload, report_uuid }) {
    const help_url =
        "https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook"
    const teams_hyperlink = <HyperLink url={help_url}>Microsoft Teams</HyperLink>
    return (
        <Segment vertical key={destination_uuid}>
            <Grid stackable>
                <Grid.Row columns={2}>
                    <Grid.Column width={6}>
                        <StringInput
                            requiredPermissions={[EDIT_REPORT_PERMISSION]}
                            id={destination_uuid}
                            label="Name"
                            set_value={(value) => {
                                set_notification_destination_attributes(
                                    report_uuid,
                                    destination_uuid,
                                    { name: value },
                                    reload,
                                )
                            }}
                            value={destination.name}
                        />
                    </Grid.Column>
                    <Grid.Column width={10}>
                        <StringInput
                            requiredPermissions={[EDIT_REPORT_PERMISSION]}
                            label={
                                <LabelWithHelp
                                    label="Webhook"
                                    help={<>Paste a {teams_hyperlink} webhook URL here.</>}
                                    hoverable
                                />
                            }
                            placeholder="https://example.webhook.office.com/webhook..."
                            set_value={(value) => {
                                set_notification_destination_attributes(
                                    report_uuid,
                                    destination_uuid,
                                    { webhook: value, url: window.location.href },
                                    reload,
                                )
                            }}
                            value={destination.webhook}
                        />
                    </Grid.Column>
                </Grid.Row>
                <ReadOnlyOrEditable
                    requiredPermissions={[EDIT_REPORT_PERMISSION]}
                    editableComponent={
                        <Grid.Row>
                            <Grid.Column>
                                <DeleteButton
                                    itemType="notification destination"
                                    onClick={() =>
                                        delete_notification_destination(
                                            report_uuid,
                                            destination_uuid,
                                            reload,
                                        )
                                    }
                                />
                            </Grid.Column>
                        </Grid.Row>
                    }
                />
            </Grid>
        </Segment>
    )
}
NotificationDestination.propTypes = {
    destination: destinationPropType,
    destination_uuid: string,
    reload: func,
    report_uuid: string,
}

export function NotificationDestinations({ destinations, reload, report_uuid }) {
    const notification_destinations = []
    Object.entries(destinations).forEach(([destination_uuid, destination]) => {
        notification_destinations.push(
            <NotificationDestination
                key={destination_uuid}
                report_uuid={report_uuid}
                destination_uuid={destination_uuid}
                destination={destination}
                reload={reload}
            />,
        )
    })
    return (
        <>
            {notification_destinations.length === 0 ? (
                <Message>
                    <Message.Header>No notification destinations</Message.Header>
                    <p>No notification destinations have been configured yet.</p>
                </Message>
            ) : (
                notification_destinations
            )}
            <ReadOnlyOrEditable
                key="1"
                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                editableComponent={
                    <Segment vertical>
                        <AddButton
                            itemType="notification destination"
                            onClick={() => add_notification_destination(report_uuid, reload)}
                        />
                    </Segment>
                }
            />
        </>
    )
}
NotificationDestinations.propTypes = {
    destinations: objectOf(destinationPropType),
    reload: func,
    report_uuid: string,
}
