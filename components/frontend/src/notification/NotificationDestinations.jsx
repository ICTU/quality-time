import { Stack } from "@mui/material"
import Grid from "@mui/material/Grid"
import { func, objectOf, string } from "prop-types"
import { useContext } from "react"

import {
    addNotificationDestination,
    deleteNotificationDestination,
    setNotificationDestinationAttributes,
} from "../api/notification"
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions, ReadOnlyOrEditable } from "../context/Permissions"
import { TextField } from "../fields/TextField"
import { destinationPropType } from "../sharedPropTypes"
import { ButtonRow } from "../widgets/ButtonRow"
import { AddButton } from "../widgets/buttons/AddButton"
import { DeleteButton } from "../widgets/buttons/DeleteButton"
import { HyperLink } from "../widgets/HyperLink"
import { InfoMessage } from "../widgets/WarningMessage"

function NotificationDestination({ destination, destinationUuid, reload, reportUuid }) {
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const helpUrl =
        "https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook"
    const teamsHyperlink = <HyperLink url={helpUrl}>Microsoft Teams webhook URL</HyperLink>
    return (
        <Stack key={destinationUuid} direction="column" spacing={2}>
            <Grid container spacing={2}>
                <Grid size={4}>
                    <TextField
                        disabled={disabled}
                        id={destinationUuid}
                        label="Webhook name"
                        onChange={(value) => {
                            setNotificationDestinationAttributes(reportUuid, destinationUuid, { name: value }, reload)
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
                            setNotificationDestinationAttributes(
                                reportUuid,
                                destinationUuid,
                                { webhook: value, url: globalThis.location.href },
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
                                onClick={() => deleteNotificationDestination(reportUuid, destinationUuid, reload)}
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
    destinationUuid: string,
    reload: func,
    reportUuid: string,
}

export function NotificationDestinations({ destinations, reload, reportUuid }) {
    const notificationDestinations = []
    for (const [destinationUuid, destination] of Object.entries(destinations)) {
        notificationDestinations.push(
            <NotificationDestination
                key={destinationUuid}
                reportUuid={reportUuid}
                destinationUuid={destinationUuid}
                destination={destination}
                reload={reload}
            />,
        )
    }
    return (
        <Stack direction="column" spacing={1}>
            {notificationDestinations.length === 0 ? (
                <InfoMessage title="No notification destinations">
                    No notification destinations have been configured yet.
                </InfoMessage>
            ) : (
                notificationDestinations
            )}
            <ReadOnlyOrEditable
                key="1"
                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                editableComponent={
                    <ButtonRow paddingLeft={0}>
                        <AddButton
                            itemType="notification destination"
                            onClick={() => addNotificationDestination(reportUuid, reload)}
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
    reportUuid: string,
}
