import React from 'react';
import { Grid, Header, Icon } from 'semantic-ui-react';
import { MetricComment } from './MetricComment';
import { MetricDebtTarget } from './MetricDebtTarget';
import { MetricTarget } from './MetricTarget';
import { MetricType } from './MetricType';
import { StringInput } from './fields/StringInput';
import { SingleChoiceInput } from './fields/SingleChoiceInput';
import { MultipleChoiceInput } from './fields/MultipleChoiceInput';

function MetricParameters(props) {
    const metric_type = props.datamodel.metrics[props.metric.type];
    const metric_unit = props.metric.unit || metric_type.unit;
    let tags = new Set();
    Object.values(props.datamodel.metrics).forEach((metric) => {metric.tags.forEach((tag) => tags.add(tag))});
    props.metric.tags.forEach((tag) => tags.add(tag));
    return (
        <>
            <Header>
                <Header.Content>
                    {metric_type.name}
                    <Header.Subheader>
                        {metric_type.description}
                    </Header.Subheader>
                </Header.Content>
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
                        <StringInput
                            label="Metric name"
                            placeholder={metric_type.name}
                            readOnly={props.readOnly}
                            set_value={(value) => props.set_metric_attribute("name", value)}
                            value={props.metric.name}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <StringInput
                            label="Metric unit"
                            placeholder={metric_type.unit}
                            readOnly={props.readOnly}
                            set_value={(value) => props.set_metric_attribute("unit", value)}
                            value={props.metric.unit}
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
                        <SingleChoiceInput
                            label={<label>Accept technical debt? <a href="https://en.wikipedia.org/wiki/Technical_debt"><Icon name="help circle" link /></a></label>}
                            value={props.metric.accept_debt}
                            options={[
                                { key: true, text: "Yes", value: true },
                                { key: false, text: "No", value: false }]}
                            readOnly={props.readOnly}
                            set_value={(value) => props.set_metric_attribute("accept_debt", value)}
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
                <Grid.Row columns={3}>
                    <Grid.Column>
                        <MultipleChoiceInput
                            allowAdditions
                            label="Tags"
                            options={[...tags]}
                            readOnly={props.readOnly}
                            set_value={(value) => props.set_metric_attribute("tags", value)}
                            value={props.metric.tags}
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
