import { Stack } from "@mui/material"
import Grid from "@mui/material/Grid2"
import { func, objectOf, string } from "prop-types"
import { useContext } from "react"

import {
    add_notification_destination,
    delete_notification_destination,
    set_notification_destination_attributes,
} from "../api/notification"
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions, ReadOnlyOrEditable } from "../context/Permissions"
import { TextField } from "../fields/TextField"
import { destinationPropType } from "../sharedPropTypes"
import { ButtonRow } from "../widgets/ButtonRow"
import { AddButton } from "../widgets/buttons/AddButton"
import { DeleteButton } from "../widgets/buttons/DeleteButton"
import { HyperLink } from "../widgets/HyperLink"
import { InfoMessage } from "../widgets/WarningMessage"

function NotificationDestination({ destination, destination_uuid, reload, report_uuid }) {
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const helpUrl =
        "https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook"
    const teamsHyperlink = <HyperLink url={helpUrl}>Microsoft Teams webhook URL</HyperLink>
    return (
        <Stack key={destination_uuid} direction="column" spacing={2}>
            <Grid container spacing={2}>
                <Grid size={4}>
                    <TextField
                        disabled={disabled}
                        id={destination_uuid}
                        label="Webhook name"
                        onChange={(value) => {
                            set_notification_destination_attributes(
                                report_uuid,
                                destination_uuid,
                                { name: value },
                                reload,
                            )
                        }}
                        value={destination.name}
                    />
                </Grid>
                <Grid size={8}>
                    <TextField
                        disabled={disabled}
                        helperText={<>Paste a {teamsHyperlink} here.</>}
                        label="Webhook"
                        onChange={(value) => {
                            set_notification_destination_attributes(
                                report_uuid,
                                destination_uuid,
                                { webhook: value, url: window.location.href },
                                reload,
                            )
                        }}
                        placeholder="https://example.webhook.office.com/webhook..."
                        value={destination.webhook}
                    />
                </Grid>
            </Grid>
            <ReadOnlyOrEditable
                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                editableComponent={
                    <ButtonRow
                        paddingRight={0}
                        rightButton={
                            <DeleteButton
                                itemType="notification destination"
                                onClick={() => delete_notification_destination(report_uuid, destination_uuid, reload)}
                            />
                        }
                    />
                }
            />
        </Stack>
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
        <Stack direction="column" spacing={1}>
            {notification_destinations.length === 0 ? (
                <InfoMessage title="No notification destinations">
                    No notification destinations have been configured yet.
                </InfoMessage>
            ) : (
                notification_destinations
            )}
            <ReadOnlyOrEditable
                key="1"
                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                editableComponent={
                    <ButtonRow paddingLeft={0}>
                        <AddButton
                            itemType="notification destination"
                            onClick={() => add_notification_destination(report_uuid, reload)}
                        />
                    </ButtonRow>
                }
            />
        </Stack>
    )
}
NotificationDestinations.propTypes = {
    destinations: objectOf(destinationPropType),
    reload: func,
    report_uuid: string,
}
