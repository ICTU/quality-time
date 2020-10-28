import React from 'react';
import { Grid, Icon } from 'semantic-ui-react';
import { StringInput } from '../fields/StringInput';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';
import { ChangeLog } from '../changelog/ChangeLog';
import { DeleteButton, DownloadAsPDFButton, DeleteNotificationDestinationButton, AddNotificationDestinationButton } from '../widgets/Button';
import { delete_report, set_report_attribute } from '../api/report';
import { add_notification_destination, delete_notification_destination, set_notification_destination_attribute } from '../api/notification'
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { HyperLink } from '../widgets/HyperLink';

export function ReportTitle(props) {
    const report_uuid = props.report.report_uuid;
    const destinations = props.report.destinations;
    function ButtonRow() {
        return (
            <Grid.Row>
                <Grid.Column>
                    <DownloadAsPDFButton report_uuid={report_uuid} query_string={props.history.location.search} />
                    <ReadOnlyOrEditable editableComponent={
                        <DeleteButton
                            item_type='report'
                            onClick={() => delete_report(report_uuid, props.go_home)}
                        />}
                    />
                </Grid.Column>
            </Grid.Row>
        )
    }
    function ReportAttributesRow() {
        return (
            <Grid.Row columns={2}>
                <Grid.Column>
                    <StringInput
                        label="Report title"
                        set_value={(value) => set_report_attribute(report_uuid, "title", value, props.reload)}
                        value={props.report.title}
                    />
                </Grid.Column>
                <Grid.Column>
                    <StringInput
                        label="Report subtitle"
                        set_value={(value) => set_report_attribute(report_uuid, "subtitle", value, props.reload)}
                        value={props.report.subtitle}
                    />
                </Grid.Column>
            </Grid.Row>
        )
    }
    function NotifierRow() {
        const help_url = "https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook";
        const label = <label>Microsoft Teams webhook <HyperLink url={help_url}><Icon name="help circle" link /></HyperLink></label>;
        const result = [];
        for (const destination of destinations) {
            result.push(
                <Grid.Row columns={3}>
                    <Grid.Column>
                        <StringInput
                            id={destination.destination.destination_uuid}
                            label='Name'
                        />
                        <StringInput
                            label={label}
                            set_value={(value) => {
                                set_notification_destination_attribute(report_uuid, destination.destination_uuid, "teams_webhook", value).then(
                                set_notification_destination_attribute(report_uuid, destination.destination_uuid, "url", window.location.href).then(
                                set_notification_destination_attribute(report_uuid, destination.destination_uuid, "name", "")))
                            }}
                            value={props.report.teams_webhook}
                        />
                        <DeleteNotificationDestinationButton
                            item_type='notification destination'
                            onClick={() => delete_notification_destination(report_uuid, destination.destination_uuid)}
                        />
                    </Grid.Column>
                </Grid.Row>
            )
        }
        result.push(
            <Grid.Row>
                <Grid.Column>
                    <AddNotificationDestinationButton
                        onClick={() => add_notification_destination(report_uuid)}
                    />
                </Grid.Column>
            </Grid.Row>
        )
        return (
            <Grid.Row>
                {result}
            </Grid.Row>
        )
    }
    function ChangeLogRow() {
        return (
            <Grid.Row>
                <Grid.Column>
                    <ChangeLog report_uuid={report_uuid} timestamp={props.report.timestamp} />
                </Grid.Column>
            </Grid.Row>
        )
    }
    return (
        <HeaderWithDetails level="h1" header={props.report.title} subheader={props.report.subtitle}>
            <Grid stackable>
                <ReportAttributesRow />
                <NotifierRow />
                <ChangeLogRow />
                <ButtonRow />
            </Grid>
        </HeaderWithDetails>
    )
}
