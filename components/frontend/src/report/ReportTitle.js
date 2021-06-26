import React from 'react';
import { Grid } from 'semantic-ui-react';
import { StringInput } from '../fields/StringInput';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';
import { ChangeLog } from '../changelog/ChangeLog';
import { DeleteButton, DownloadAsPDFButton } from '../widgets/Button';
import { delete_report, set_report_attribute } from '../api/report';
import { EDIT_REPORT_PERMISSION, ReadOnlyOrEditable } from '../context/Permissions';
import { NotificationDestinations } from '../notification/NotificationDestinations';

function ReportAttributesRow(props) {
    return (
        <Grid.Row columns={2}>
            <Grid.Column>
                <StringInput
                    requiredPermissions={[EDIT_REPORT_PERMISSION]}
                    id="report-title"
                    label="Report title"
                    set_value={(value) => set_report_attribute(props.report_uuid, "title", value, props.reload)}
                    value={props.title}
                />
            </Grid.Column>
            <Grid.Column>
                <StringInput
                    requiredPermissions={[EDIT_REPORT_PERMISSION]}
                    id="report-subtitle"
                    label="Report subtitle"
                    set_value={(value) => set_report_attribute(props.report_uuid, "subtitle", value, props.reload)}
                    value={props.subtitle}
                />
            </Grid.Column>
        </Grid.Row>
    )
}

function NotificationDestinationsRow(props) {
    return (
        <Grid.Row>
            <Grid.Column>
                <NotificationDestinations {...props} />
            </Grid.Column>
        </Grid.Row>
    )
}

function ChangeLogRow(props) {
    return (
        <Grid.Row>
            <Grid.Column>
                <ChangeLog {...props} />
            </Grid.Column>
        </Grid.Row>
    )
}

function ButtonRow(props) {
    return (
        <Grid.Row>
            <Grid.Column>
                <DownloadAsPDFButton report_uuid={props.report_uuid} history={props.history} />
                <ReadOnlyOrEditable requiredPermissions={[EDIT_REPORT_PERMISSION]} editableComponent={
                    <DeleteButton
                        item_type='report'
                        onClick={() => delete_report(props.report_uuid, props.go_home)}
                    />}
                />
            </Grid.Column>
        </Grid.Row>
    )
}

export function ReportTitle(props) {
    const report_uuid = props.report.report_uuid;
    return (
        <HeaderWithDetails level="h1" header={props.report.title} subheader={props.report.subtitle}>
            <Grid stackable>
                <ReportAttributesRow report_uuid={report_uuid} reload={props.reload} title={props.report.title} subtitle={props.report.subtitle} />
                <NotificationDestinationsRow destinations={props.report.notification_destinations || {}} report_uuid={report_uuid} reload={props.reload} />
                <ChangeLogRow report_uuid={report_uuid} timestamp={props.report.timestamp} />
                <ButtonRow report_uuid={report_uuid} go_home={props.go_home} history={props.history} />
            </Grid>
        </HeaderWithDetails>
    )
}
