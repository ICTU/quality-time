import React from 'react';
import { Grid, Icon } from 'semantic-ui-react';
import { StringInput } from '../fields/StringInput';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';
import { ChangeLog } from '../changelog/ChangeLog';
import { AddButton, DeleteButton, DownloadAsPDFButton } from '../widgets/Button';
import { delete_report, set_report_attribute } from '../api/report';
import { add_notification_destination, delete_notification_destination, set_notification_destination_attributes } from '../api/notification'
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { HyperLink } from '../widgets/HyperLink';

export function ReportTitle(props) {
    const report_uuid = props.report.report_uuid;
    const destinations = props.report.notification_destinations;
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
        if(destinations){
            Object.entries(destinations).forEach(([destination_uuid, destination]) => {
                result.push(
                    <Grid.Row columns={3}>
                        <Grid.Column>
                            <StringInput
                                id={destination_uuid}
                                label='Name'
                                set_value={(value) => {
                                    set_notification_destination_attributes(report_uuid, destination_uuid, {name: value}, props.reload)
                                }}
                                value={destination.name}
                            />
                            <StringInput
                                label={label}
                                set_value={(value) => {
                                    set_notification_destination_attributes(report_uuid, destination_uuid, {teams_webhook: value, url: window.location.href}, props.reload)
                                }}
                                value={destination.teams_webhook}
                            />
                            <DeleteButton
                                item_type='notification destination'
                                onClick={() => delete_notification_destination(report_uuid, destination_uuid)}
                            />
                        </Grid.Column>
                    </Grid.Row>
                )
            })
        }
        result.push(
            <Grid stackable>
                <Grid.Row>
                    <Grid.Column>
                        <AddButton
                            item_type="notification destinations"
                            report_uuid={report_uuid}
                            onClick={() => add_notification_destination(report_uuid, props.reload)}
                        />
                    </Grid.Column>
                </Grid.Row>
            </Grid>
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
