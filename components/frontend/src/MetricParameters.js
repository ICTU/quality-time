import React from 'react';
import { Grid, Message } from 'semantic-ui-react';
import { MetricComment } from './MetricComment';
import { MetricName } from './MetricName';
import { MetricTarget } from './MetricTarget';
import { MetricType } from './MetricType';

function MetricParameters(props) {
    const metric_type = props.datamodel.metrics[props.metric.type];
    return (
        <Grid stackable>
            <Grid.Row columns={1}>
                <Grid.Column>
                    <Message fluid header={metric_type.name} content={metric_type.description} />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row columns={3}>
                <Grid.Column>
                    <MetricType report_uuid={props.report_uuid} metric_uuid={props.metric_uuid}
                        user={props.user} datamodel={props.datamodel} metric_type={props.metric.type}
                        reload={props.reload} />
                </Grid.Column>
                <Grid.Column>
                    <MetricName report_uuid={props.report_uuid} metric_uuid={props.metric_uuid}
                        user={props.user} datamodel={props.datamodel} metric_name={props.metric.name}
                        metric_type_name={metric_type.name} reload={props.reload} />
                </Grid.Column>
                <Grid.Column>
                    <MetricTarget report_uuid={props.report_uuid} metric_uuid={props.metric_uuid}
                        unit={metric_type.unit} direction={metric_type.direction}
                        user={props.user} set_target={props.set_target} target={props.metric.target} />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row columns={1}>
                <Grid.Column>
                    <MetricComment report_uuid={props.report_uuid} metric_uuid={props.metric_uuid}
                        user={props.user} comment={props.metric.comment} reload={props.reload} />
                </Grid.Column>
            </Grid.Row>
        </Grid>
    )
}

export { MetricParameters };
