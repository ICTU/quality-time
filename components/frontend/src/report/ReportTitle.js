import React, { useState } from 'react';
import { Grid } from 'semantic-ui-react';
import { StringInput } from '../fields/StringInput';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';
import { ChangeLog } from '../changelog/ChangeLog';
import { CopyButton, DeleteButton, DownloadAsPDFButton } from '../widgets/Button';
import { copy_report, delete_report, get_report_pdf, set_report_attribute } from '../api/report';
import { ReadOnlyOrEditable } from '../context/ReadOnly';
import { IntegerInput } from '../fields/IntegerInput';

function download_pdf(report_uuid, callback) {
    get_report_pdf(report_uuid)
        .then(pdf => {
            let url = window.URL.createObjectURL(pdf);
            let a = document.createElement('a');
            a.href = url;
            let now = new Date();
            a.download = `Quality-time-report-${report_uuid}-${now.toISOString()}.pdf`;
            a.click();
        }).finally(() => callback());
}

export function ReportTitle(props) {
    const [loading, setLoading] = useState(false);
    function ButtonRow() {
        return (
            <Grid.Row>
                <Grid.Column>
                    <DownloadAsPDFButton
                        loading={loading}
                        onClick={() => {
                            if (!loading) {
                                setLoading(true);
                                download_pdf(props.report.report_uuid, () => { setLoading(false) })
                            }
                        }}
                    />
                    <ReadOnlyOrEditable editableComponent={
                        <CopyButton
                            item_type="report"
                            onClick={() => copy_report(props.report.report_uuid, props.reload)}
                        />}
                    />
                    <ReadOnlyOrEditable editableComponent={
                        <DeleteButton
                            item_type='report'
                            onClick={() => delete_report(props.report.report_uuid, props.go_home)}
                        />}
                    />
                </Grid.Column>
            </Grid.Row>
        )
    }
    function ReportAttributesRow() {
        return (
            <Grid.Row columns={3}>
                <Grid.Column>
                    <StringInput
                        label="Report title"
                        set_value={(value) => set_report_attribute(props.report.report_uuid, "title", value, props.reload)}
                        value={props.report.title}
                    />
                </Grid.Column>
                <Grid.Column>
                    <StringInput
                        label="Report subtitle"
                        set_value={(value) => set_report_attribute(props.report.report_uuid, "subtitle", value, props.reload)}
                        value={props.report.subtitle}
                    />
                </Grid.Column>
                <Grid.Column>
                    <IntegerInput
                        label="Delay before generating PDF"
                        min="1"
                        set_value={(value) => set_report_attribute(props.report.report_uuid, "delay", value, props.reload)}
                        unit="second(s)"
                        value={props.report.delay || 5} />
                </Grid.Column>
            </Grid.Row>
        )
    }
    function ChangeLogRow() {
        return (
            <Grid.Row>
                <Grid.Column>
                    <ChangeLog report_uuid={props.report.report_uuid} timestamp={props.report.timestamp} />
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
