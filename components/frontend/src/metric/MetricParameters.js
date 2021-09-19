import React from 'react';
import { Grid, Header, Icon, Popup } from 'semantic-ui-react';
import { MetricType } from './MetricType';
import { MultipleChoiceInput } from '../fields/MultipleChoiceInput';
import { StringInput } from '../fields/StringInput';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';
import { Comment } from '../fields/Comment';
import { set_metric_attribute } from '../api/metric';
import { DateInput } from '../fields/DateInput';
import { HyperLink } from '../widgets/HyperLink';
import { Target } from './Target';
import { EDIT_REPORT_PERMISSION } from '../context/Permissions';
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

export function MetricParameters({ datamodel, report, metric, metric_uuid, reload }) {
    const metric_type = datamodel.metrics[metric.type];
    const metric_scale = metric.scale || metric_type.default_scale || "count";
    const metric_unit_without_percentage = metric.unit || metric_type.unit;
    const metric_unit = `${metric_scale === "percentage" ? "% " : ""}${metric_unit_without_percentage}`;
    const fewer = { count: `Fewer ${metric_unit}`, percentage: `A lower percentage of ${metric_unit_without_percentage}`, version_number: "A lower version number" }[metric_scale];
    const more = { count: `More ${metric_unit}`, percentage: `A higher percentage of ${metric_unit_without_percentage}`, version_number: "A higher version number" }[metric_scale];
    // Old versions of the datamodel may contain the unicode version of the direction, be prepared:
    const metric_direction = { "≦": "<", "≧": ">", "<": "<", ">": ">" }[metric.direction || metric_type.direction];
    const tags = Object.keys(report.summary_by_tag || {});
    const scale_options = metric_scale_options(metric_type.scales || ["count"], datamodel);
    let issue_status_error = false;
    if (metric.issue_status?.connection_error) {
        issue_status_error = {content: "Connection error retrieving the issue status: " + metric.issue_status.connection_error};
    }
    if (metric.issue_status?.parse_error) {
        issue_status_error = {content: "Parse error retrieving the issue status: " + metric.issue_status.parse_error};
    }
    const issue_status_help = "An issue that tracks the progress of fixing this metric." + (report.issue_tracker ? "" : " Please configure an issue tracker by expanding the report title and selecting the 'Issue tracker' tab.");
    return (
        <Grid stackable columns={3}>
            <Grid.Row>
                <Grid.Column>
                    <MetricType
                        datamodel={datamodel}
                        metric_type={metric.type}
                        metric_uuid={metric_uuid}
                        reload={reload}
                    />
                </Grid.Column>
                <Grid.Column>
                    <StringInput
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label="Metric name"
                        placeholder={metric_type.name}
                        set_value={(value) => set_metric_attribute(metric_uuid, "name", value, reload)}
                        value={metric.name}
                    />
                </Grid.Column>
                <Grid.Column>
                    <MultipleChoiceInput
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        allowAdditions
                        label="Tags"
                        options={[...tags]}
                        set_value={(value) => set_metric_attribute(metric_uuid, "tags", value, reload)}
                        value={get_metric_tags(metric)}
                    />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row>
                <Grid.Column>
                    <SingleChoiceInput
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label="Metric scale"
                        options={scale_options}
                        placeholder={metric_type.default_scale || "Count"}
                        set_value={(value) => set_metric_attribute(metric_uuid, "scale", value, reload)}
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
                        set_value={(value) => set_metric_attribute(metric_uuid, "direction", value, reload)}
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
                            set_value={(value) => set_metric_attribute(metric_uuid, "unit", value, reload)}
                            value={metric.unit}
                        />
                    </Grid.Column>}
            </Grid.Row>
            <Grid.Row>
                <Grid.Column>
                    <Target
                        label="Metric target"
                        target_type="target"
                        datamodel={datamodel}
                        metric={metric}
                        metric_uuid={metric_uuid}
                        reload={reload}
                    />
                </Grid.Column>
                <Grid.Column>
                    <Target
                        label="Metric near target"
                        target_type="near_target"
                        datamodel={datamodel}
                        metric={metric}
                        metric_uuid={metric_uuid}
                        reload={reload}
                    />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row>
                <Grid.Column>
                    <SingleChoiceInput
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label={<label>Accept technical debt? <HyperLink url="https://en.wikipedia.org/wiki/Technical_debt"><Icon name="help circle" link /></HyperLink></label>}
                        value={metric.accept_debt || false}
                        options={[
                            { key: true, text: "Yes", value: true },
                            { key: false, text: "No", value: false }]}
                        set_value={(value) => set_metric_attribute(metric_uuid, "accept_debt", value, reload)}
                    />
                </Grid.Column>
                <Grid.Column>
                    <Target
                        label="Accepted technical debt"
                        target_type="debt_target"
                        datamodel={datamodel}
                        metric={metric}
                        metric_uuid={metric_uuid}
                        reload={reload}
                    />
                </Grid.Column>
                <Grid.Column>
                    <DateInput
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label="Technical debt end date"
                        placeholder="no end date"
                        set_value={(value) => set_metric_attribute(metric_uuid, "debt_end_date", value, reload)}
                        value={metric.debt_end_date || ""}
                    />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row columns="equal">
                <Grid.Column width={4}>
                    <StringInput
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        label={<label>Issue ID <Popup on={['hover', 'focus']} content={issue_status_help} trigger={<Icon tabIndex="0" name="help circle"/>}/></label>}
                        placeholder="Issue ID"
                        set_value={(value) => set_metric_attribute(metric_uuid, "issue_id", [value], reload)}
                        value={metric.issue_id}
                        error={issue_status_error}
                    />
                </Grid.Column>
                <Grid.Column stretched>
                    <Comment
                        requiredPermissions={[EDIT_REPORT_PERMISSION]}
                        set_value={(value) => set_metric_attribute(metric_uuid, "comment", value, reload)}
                        value={metric.comment}
                    />
                </Grid.Column>
            </Grid.Row>
        </Grid>
    );
}
