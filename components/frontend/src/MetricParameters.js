import React from 'react';
import { Grid } from 'semantic-ui-react';
import { MetricComment } from './MetricComment';
import { MetricName } from './MetricName';
import { MetricTarget } from './MetricTarget';
import { MetricType } from './MetricType';

function MetricParameters(props) {
    const metric_type = props.datamodel.metrics[props.metric.type];
    const metric_name = props.metric.name || metric_type.name;
    return (
        <Grid stackable>
            <Grid.Row columns={3}>
                <Grid.Column>
                    <MetricName report_uuid={props.report_uuid} metric_uuid={props.metric_uuid}
                        datamodel={props.datamodel} metric_name={metric_name} reload={props.reload} />
                </Grid.Column>
                <Grid.Column>
                    <MetricType report_uuid={props.report_uuid} metric_uuid={props.metric_uuid}
                        datamodel={props.datamodel} metric_type={props.metric.type} reload={props.reload} />
                </Grid.Column>
                <Grid.Column>
                    <MetricTarget report_uuid={props.report_uuid} metric_uuid={props.metric_uuid}
                        unit={metric_type.unit} direction={metric_type.direction} reload={props.reload}
                        target={props.metric.target} />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row columns={1}>
                <Grid.Column>
                    <MetricComment report_uuid={props.report_uuid} metric_uuid={props.metric_uuid}
                        comment={props.metric.comment} reload={props.reload} />
                </Grid.Column>
            </Grid.Row>
        </Grid>
    )
}

export { MetricParameters };
