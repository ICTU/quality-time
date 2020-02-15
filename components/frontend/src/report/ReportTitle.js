import React from 'react';
import { Grid } from 'semantic-ui-react';
import { StringInput } from '../fields/StringInput';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';
import { ChangeLog } from '../changelog/ChangeLog';
import { CopyButton, DeleteButton, DownloadAsPDFButton } from '../widgets/Button';
import { copy_report, delete_report, set_report_attribute } from '../api/report';
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { IntegerInput } from '../fields/IntegerInput';

export function ReportTitle(props) {
    const report_uuid = props.report.report_uuid;
    function ButtonRow() {
        return (
            <Grid.Row>
                <Grid.Column>
                    <DownloadAsPDFButton report_uuid={report_uuid} />
                    <ReadOnlyOrEditable editableComponent={
                        <CopyButton
                            item_type="report"
                            onClick={() => copy_report(report_uuid, props.reload)}
                        />}
                    />
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
                <ChangeLogRow />
                <ButtonRow />
            </Grid>
        </HeaderWithDetails>
    )
}
