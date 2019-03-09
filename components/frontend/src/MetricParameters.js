import React from 'react';
import { Grid, Message } from 'semantic-ui-react';
import { MetricComment } from './MetricComment';
import { MetricDebtTarget } from './MetricDebtTarget';
import { MetricTarget } from './MetricTarget';
import { MetricType } from './MetricType';
import { StringParameter } from './StringParameter';

function MetricParameters(props) {
    const metric_type = props.datamodel.metrics[props.metric.type];
    return (
        <Grid stackable>
            <Grid.Row columns={1}>
                <Grid.Column>
                    <Message header={metric_type.name} content={metric_type.description} />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row columns={3}>
                <Grid.Column>
                    <MetricType datamodel={props.datamodel} metric_type={props.metric.type}
                        set_metric_attribute={props.set_metric_attribute} readOnly={props.user === null} />
                </Grid.Column>
                <Grid.Column>
                    <StringParameter
                        parameter_key="name" parameter_name={"Metric name"} parameter_value={props.metric.name}
                        set_parameter={props.set_metric_attribute}
                        placeholder={metric_type.name} readOnly={props.user === null} />
                </Grid.Column>
                <Grid.Column>
                    <MetricTarget unit={metric_type.unit} direction={metric_type.direction}
                        user={props.user} set_metric_attribute={props.set_metric_attribute} target={props.metric.target} />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row columns={1}>
                <Grid.Column>
                    <MetricDebtTarget
                        unit={metric_type.unit} direction={metric_type.direction}
                        user={props.user} set_metric_attribute={props.set_metric_attribute} target={props.metric.debt_target} />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row columns={1}>
                <Grid.Column>
                    <MetricComment
                        user={props.user} comment={props.metric.comment} set_metric_attribute={props.set_metric_attribute} />
                </Grid.Column>
            </Grid.Row>
        </Grid>
    )
}

export { MetricParameters };
