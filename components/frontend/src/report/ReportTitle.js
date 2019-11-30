import React, { useState} from 'react';
import { Button, Grid, Icon, Segment } from 'semantic-ui-react';
import { StringInput } from '../fields/StringInput';
import { HeaderWithDetails } from '../widgets/HeaderWithDetails';
import { ChangeLog } from '../changelog/ChangeLog';
import { delete_report, get_report_pdf, set_report_attribute} from '../api/report';

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
    return (
        <HeaderWithDetails level="h1" header={props.report.title} subheader={props.report.subtitle}>
            <Segment>
                <Grid stackable>
                    <Grid.Row columns={3}>
                        <Grid.Column>
                            <StringInput
                                label="Report title"
                                readOnly={props.readOnly}
                                set_value={(value) => set_report_attribute(props.report.report_uuid, "title", value, props.reload)}
                                value={props.report.title}
                            />
                        </Grid.Column>
                        <Grid.Column>
                            <StringInput
                                label="Report subtitle"
                                readOnly={props.readOnly}
                                set_value={(value) => set_report_attribute(props.report.report_uuid, "subtitle", value, props.reload)}
                                value={props.report.subtitle}
                            />
                        </Grid.Column>
                    </Grid.Row>
                    <Grid.Row>
                        <Grid.Column>
                            <ChangeLog
                               report_uuid={props.report.report_uuid}
                               timestamp={props.report.timestamp}
                            />
                        </Grid.Column>
                    </Grid.Row>
                    {!props.readOnly &&
                        <Grid.Row>
                            <Grid.Column>
                                <Button
                                    basic
                                    floated="left"
                                    icon
                                    loading={loading}
                                    onClick={() => {
                                        if (!loading) {
                                            setLoading(true);
                                            download_pdf(props.report.report_uuid, () => {setLoading(false)})}
                                        }
                                    }
                                    primary
                                >
                                    <Icon name="file pdf" /> Download report as pdf
                                </Button>
                                <Button
                                    basic
                                    floated='right'
                                    negative
                                    icon
                                    onClick={() => delete_report(props.report.report_uuid, props.go_home)}
                                    primary
                                >
                                    <Icon name='trash' /> Delete report
                                </Button>
                            </Grid.Column>
                        </Grid.Row>
                    }
                </Grid>
            </Segment>
        </HeaderWithDetails>
    )
}
