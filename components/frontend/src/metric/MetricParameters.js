import React from 'react';
import { Grid, Header, Icon } from 'semantic-ui-react';
import { MetricType } from './MetricType';
import { IntegerInput } from '../fields/IntegerInput';
import { MultipleChoiceInput } from '../fields/MultipleChoiceInput';
import { StringInput } from '../fields/StringInput';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';
import { Comment } from '../fields/Comment';
import { set_metric_attribute } from '../api/metric';
import { DateInput } from '../fields/DateInput';

function metric_scale_options(metric_scales, datamodel) {
    let scale_options = [];
    metric_scales.forEach((scale) => {
        let scale_name = datamodel.scales ? datamodel.scales[scale].name : "Count";
        let scale_description = datamodel.scales ? datamodel.scales[scale].description : "";
        scale_options.push(
            {
                content: <Header as="h4" content={scale_name} subheader={scale_description} />,
                key: scale,
                text: scale_name,
                value: scale
            })
    });
    return scale_options;
}

function combine_tags(metric, datamodel) {
    let tags = new Set();
    Object.values(datamodel.metrics).forEach((metric) => { metric.tags.forEach((tag) => tags.add(tag)) });
    metric.tags.forEach((tag) => tags.add(tag));
    return tags;
}

export function MetricParameters(props) {
    const metric_type = props.datamodel.metrics[props.metric.type];
    const metric_scale = props.metric.scale || metric_type.default_scale || "count";
    const metric_unit_without_percentage = props.metric.unit || metric_type.unit;
    const metric_unit = `${metric_scale === "percentage" ? "% " : ""}${metric_unit_without_percentage}`;
    const fewer = metric_scale === "percentage" ? `A lower percentage of ${metric_unit_without_percentage}` : `Fewer ${metric_unit}`;
    const more = metric_scale === "percentage" ? `A higher percentage of ${metric_unit_without_percentage}` : `More ${metric_unit}`;
    // Old versions of the datamodel may contain the unicode version of the direction, be prepared:
    const metric_direction = { "≦": "<", "≧": ">", "<": "<", ">": ">" }[props.metric.direction || metric_type.direction];
    const metric_direction_prefix = { "<": "≦", ">": "≧" }[metric_direction];
    const max = metric_scale === "percentage" ? "100" : null;
    const tags = combine_tags(props.metric, props.datamodel);
    const scale_options = metric_scale_options(metric_type.scales || ["count"], props.datamodel);
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
                            metric_uuid={props.metric_uuid}
                            readOnly={props.readOnly}
                            reload={props.reload}
                            report_uuid={props.report_uuid}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <StringInput
                            label="Metric name"
                            placeholder={metric_type.name}
                            readOnly={props.readOnly}
                            set_value={(value) => set_metric_attribute(props.report_uuid, props.metric_uuid, "name", value, props.reload)}
                            value={props.metric.name}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <MultipleChoiceInput
                            allowAdditions
                            label="Tags"
                            options={[...tags]}
                            readOnly={props.readOnly}
                            set_value={(value) => set_metric_attribute(props.report_uuid, props.metric_uuid, "tags", value, props.reload)}
                            value={props.metric.tags}
                        />
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row columns={3}>
                    <Grid.Column>
                        <SingleChoiceInput
                            label="Metric scale"
                            options={scale_options}
                            placeholder={metric_type.default_scale || "Count"}
                            readOnly={props.readOnly}
                            set_value={(value) => set_metric_attribute(props.report_uuid, props.metric_uuid, "scale", value, props.reload)}
                            value={metric_scale}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <SingleChoiceInput
                            label="Metric direction"
                            options={[
                                { key: "0", text: `${fewer} is better`, value: "<" },
                                { key: "1", text: `${more} is better`, value: ">" }]}
                            readOnly={props.readOnly}
                            set_value={(value) => set_metric_attribute(props.report_uuid, props.metric_uuid, "direction", value, props.fetch_measurement_and_reload)}
                            value={metric_direction}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <StringInput
                            label="Metric unit"
                            placeholder={metric_type.unit}
                            prefix={metric_scale === "percentage" ? "%" : ""}
                            readOnly={props.readOnly}
                            set_value={(value) => set_metric_attribute(props.report_uuid, props.metric_uuid, "unit", value, props.reload)}
                            value={props.metric.unit}
                        />
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row columns={3}>
                    <Grid.Column>
                        <IntegerInput
                            label={'Metric target' + (metric_type.target === props.metric.target ? '' : ` (default: ${metric_type.target} ${metric_unit})`)}
                            max={max}
                            min="0"
                            prefix={metric_direction_prefix}
                            readOnly={props.readOnly}
                            set_value={(value) => set_metric_attribute(props.report_uuid, props.metric_uuid, "target", value, props.fetch_measurement_and_reload)}
                            unit={metric_unit}
                            value={props.metric.target}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <IntegerInput
                            label={'Metric near target' + (metric_type.near_target === props.metric.near_target ? '' : ` (default: ${metric_type.near_target} ${metric_unit})`)}
                            max={max}
                            min="0"
                            prefix={metric_direction_prefix}
                            readOnly={props.readOnly}
                            set_value={(value) => set_metric_attribute(props.report_uuid, props.metric_uuid, "near_target", value, props.fetch_measurement_and_reload)}
                            unit={metric_unit}
                            value={props.metric.near_target}
                        />
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row columns={3}>
                    <Grid.Column>
                        <SingleChoiceInput
                            label={<label>Accept technical debt? <a href="https://en.wikipedia.org/wiki/Technical_debt"><Icon name="help circle" link /></a></label>}
                            value={props.metric.accept_debt}
                            options={[
                                { key: true, text: "Yes", value: true },
                                { key: false, text: "No", value: false }]}
                            readOnly={props.readOnly}
                            set_value={(value) => set_metric_attribute(props.report_uuid, props.metric_uuid, "accept_debt", value, props.fetch_measurement_and_reload)}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <IntegerInput
                            label="Metric debt target"
                            max={max}
                            min="0"
                            prefix={metric_direction_prefix}
                            readOnly={props.readOnly}
                            set_value={(value) => set_metric_attribute(props.report_uuid, props.metric_uuid, "debt_target", value, props.fetch_measurement_and_reload)}
                            unit={metric_unit}
                            value={props.metric.debt_target}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <DateInput
                            label="Metric debt end date"
                            readOnly={props.readOnly}
                            set_value={(value) => set_metric_attribute(props.report_uuid, props.metric_uuid, "debt_end_date", value, props.fetch_measurement_and_reload)}
                            value={props.metric.debt_end_date || ""}
                        />
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row columns={1}>
                    <Grid.Column>
                        <Comment
                            readOnly={props.readOnly}
                            set_value={(value) => set_metric_attribute(props.report_uuid, props.metric_uuid, "comment", value, props.reload)}
                            value={props.metric.comment}
                        />
                    </Grid.Column>
                </Grid.Row>
            </Grid>
        </>
    )
}
