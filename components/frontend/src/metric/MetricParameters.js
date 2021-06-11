import React from 'react';
import { Grid, Header, Icon } from 'semantic-ui-react';
import { MetricType } from './MetricType';
import { MultipleChoiceInput } from '../fields/MultipleChoiceInput';
import { StringInput } from '../fields/StringInput';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';
import { Comment } from '../fields/Comment';
import { set_metric_attribute } from '../api/metric';
import { DateInput } from '../fields/DateInput';
import { HyperLink } from '../widgets/HyperLink';
import { Target } from './Target';
import { EDIT_REPORT_PERMISSION } from '../context/ReadOnly';
import { get_metric_tags } from '../utils';

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

export function MetricParameters(props) {
    const metric_type = props.datamodel.metrics[props.metric.type];
    const metric_scale = props.metric.scale || metric_type.default_scale || "count";
    const metric_unit_without_percentage = props.metric.unit || metric_type.unit;
    const metric_unit = `${metric_scale === "percentage" ? "% " : ""}${metric_unit_without_percentage}`;
    const fewer = {count: `Fewer ${metric_unit}`, percentage: `A lower percentage of ${metric_unit_without_percentage}`, version_number: "A lower version number"}[metric_scale];
    const more = {count: `More ${metric_unit}`, percentage: `A higher percentage of ${metric_unit_without_percentage}`, version_number: "A higher version number"}[metric_scale];
    // Old versions of the datamodel may contain the unicode version of the direction, be prepared:
    const metric_direction = { "≦": "<", "≧": ">", "<": "<", ">": ">" }[props.metric.direction || metric_type.direction];
    const tags = Object.keys(props.report.summary_by_tag || {});
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
                            reload={props.reload}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <StringInput
                            requiredPermissions={[EDIT_REPORT_PERMISSION]}
                            label="Metric name"
                            placeholder={metric_type.name}
                            set_value={(value) => set_metric_attribute(props.metric_uuid, "name", value, props.reload)}
                            value={props.metric.name}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <MultipleChoiceInput
                            requiredPermissions={[EDIT_REPORT_PERMISSION]}
                            allowAdditions
                            label="Tags"
                            options={[...tags]}
                            set_value={(value) => set_metric_attribute(props.metric_uuid, "tags", value, props.reload)}
                            value={get_metric_tags(props.metric)}
                        />
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row columns={3}>
                    <Grid.Column>
                        <SingleChoiceInput
                            requiredPermissions={[EDIT_REPORT_PERMISSION]}
                            label="Metric scale"
                            options={scale_options}
                            placeholder={metric_type.default_scale || "Count"}
                            set_value={(value) => set_metric_attribute(props.metric_uuid, "scale", value, props.reload)}
                            value={metric_scale}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <SingleChoiceInput
                            requiredPermissions={[EDIT_REPORT_PERMISSION]}
                            label="Metric direction"
                            options={[
                                { key: "0", text: `${fewer} is better`, value: "<" },
                                { key: "1", text: `${more} is better`, value: ">" }]}
                            set_value={(value) => set_metric_attribute(props.metric_uuid, "direction", value, props.reload)}
                            value={metric_direction || "<"}
                        />
                    </Grid.Column>
                    {metric_scale !== "version_number" &&
                        <Grid.Column>
                            <StringInput
                                label="Metric unit"
                                placeholder={metric_type.unit}
                                prefix={metric_scale === "percentage" ? "%" : ""}
                                requiredPermissions={[EDIT_REPORT_PERMISSION]}
                                set_value={(value) => set_metric_attribute(props.metric_uuid, "unit", value, props.reload)}
                                value={props.metric.unit}
                            />
                        </Grid.Column>}
                </Grid.Row>
                <Grid.Row columns={3}>
                    <Grid.Column>
                        <Target
                            label="Metric target"
                            target_type="target"
                            {...props}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <Target
                            label="Metric near target"
                            target_type="near_target"
                            {...props}
                        />
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row columns={3}>
                    <Grid.Column>
                        <SingleChoiceInput
                            requiredPermissions={[EDIT_REPORT_PERMISSION]}
                            label={<label>Accept technical debt? <HyperLink url="https://en.wikipedia.org/wiki/Technical_debt"><Icon name="help circle" link /></HyperLink></label>}
                            value={props.metric.accept_debt || false}
                            options={[
                                { key: true, text: "Yes", value: true },
                                { key: false, text: "No", value: false }]}
                            set_value={(value) => set_metric_attribute(props.metric_uuid, "accept_debt", value, props.reload)}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <Target
                            label="Accepted technical debt"
                            target_type="debt_target"
                            {...props}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <DateInput
                            requiredPermissions={[EDIT_REPORT_PERMISSION]}
                            label="Technical debt end date"
                            placeholder="no end date"
                            set_value={(value) => set_metric_attribute(props.metric_uuid, "debt_end_date", value, props.reload)}
                            value={props.metric.debt_end_date || ""}
                        />
                    </Grid.Column>
                </Grid.Row>
                <Grid.Row columns={1}>
                    <Grid.Column>
                        <Comment
                            requiredPermissions={[EDIT_REPORT_PERMISSION]}
                            set_value={(value) => set_metric_attribute(props.metric_uuid, "comment", value, props.reload)}
                            value={props.metric.comment}
                        />
                    </Grid.Column>
                </Grid.Row>
            </Grid>
        </>
    );
}
