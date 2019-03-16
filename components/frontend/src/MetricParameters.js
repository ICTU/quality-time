import React from 'react';
import { Grid, Header } from 'semantic-ui-react';
import { MetricComment } from './MetricComment';
import { MetricDebtTarget } from './MetricDebtTarget';
import { MetricTarget } from './MetricTarget';
import { MetricType } from './MetricType';
import { StringParameter } from './StringParameter';
import { SingleChoiceParameter } from './SingleChoiceParameter';

function MetricParameters(props) {
    const metric_type = props.datamodel.metrics[props.metric.type];
    const metric_unit = props.metric.unit || metric_type.unit;
    return (
        <>
            <Header>
                {metric_type.name}
                <Header.Subheader>
                    {metric_type.description}
                </Header.Subheader>
            </Header>
            <Grid stackable>
                <Grid.Row columns={3}>
                    <Grid.Column>
                        <MetricType
                            datamodel={props.datamodel}
                            metric_type={props.metric.type}
                            readOnly={props.readOnly}
                            set_metric_attribute={props.set_metric_attribute}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <StringParameter
                            parameter_key="name"
                            parameter_name={"Metric name"}
                            parameter_value={props.metric.name}
                            placeholder={metric_type.name}
                            readOnly={props.readOnly}
                            set_parameter={props.set_metric_attribute}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <StringParameter
                            parameter_key="unit"
                            parameter_name={"Metric unit"}
                            parameter_value={props.metric.unit}
                            placeholder={metric_type.unit}
                            readOnly={props.readOnly}
                            set_parameter={props.set_metric_attribute}
                        />
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row columns={3}>
                    <Grid.Column>
                        <MetricTarget
                            direction={metric_type.direction}
                            readOnly={props.readOnly}
                            set_metric_attribute={props.set_metric_attribute}
                            target={props.metric.target}
                            unit={metric_unit}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <SingleChoiceParameter
                            parameter_key="accept_debt"
                            parameter_name="Accept technical debt?"
                            parameter_value={props.metric.accept_debt}
                            parameter_values={[{ text: "Yes", value: true }, { text: "No", value: false }]}
                            readOnly={props.readOnly}
                            set_parameter={props.set_metric_attribute}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <MetricDebtTarget
                            direction={metric_type.direction}
                            readOnly={props.readOnly}
                            set_metric_attribute={props.set_metric_attribute}
                            target={props.metric.debt_target}
                            unit={metric_unit}
                        />
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row columns={1}>
                    <Grid.Column>
                        <MetricComment
                            comment={props.metric.comment}
                            readOnly={props.readOnly}
                            set_metric_attribute={props.set_metric_attribute}
                        />
                    </Grid.Column>
                </Grid.Row>
            </Grid>
        </>
    )
}

export { MetricParameters };
