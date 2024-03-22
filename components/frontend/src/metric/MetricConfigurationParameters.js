import { useContext } from 'react';
import { func, string } from 'prop-types';
import { Grid, Header } from 'semantic-ui-react';
import { MultipleChoiceInput } from '../fields/MultipleChoiceInput';
import { StringInput } from '../fields/StringInput';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';
import { set_metric_attribute } from '../api/metric';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION } from '../context/Permissions';
import { dropdownOptions, formatMetricScale, getMetricDirection, getMetricScale, getReportTags, getMetricTags } from '../utils';
import { LabelWithHelp } from '../widgets/LabelWithHelp';
import { MetricType } from './MetricType';
import { Target } from './Target';
import { metricPropType, reportPropType, subjectPropType } from '../sharedPropTypes';

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

function MetricName({ metric, metric_uuid, reload }) {
    const dataModel = useContext(DataModel)
    const metricType = dataModel.metrics[metric.type];
    const labelId = `metric-name-${metric_uuid}`
    return (
        <StringInput
            aria-labelledby={labelId}
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label={<label id={labelId}>Metric name</label>}
            placeholder={metricType.name}
            set_value={(value) => set_metric_attribute(metric_uuid, "name", value, reload)}
            value={metric.name ?? ""}
        />
    )
}
MetricName.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
}

function Tags({ metric, metric_uuid, reload, report }) {
    const tags = getReportTags(report)
    const labelId = `tags-${metric_uuid}`
    return (
        <MultipleChoiceInput
            allowAdditions
            aria-labelledby={labelId}
            label={<label id={labelId}>Tags</label>}
            options={dropdownOptions(tags)}
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            set_value={(value) => set_metric_attribute(metric_uuid, "tags", value, reload)}
            value={getMetricTags(metric)}
        />
    )
}
Tags.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
    report: reportPropType,
}

function Scale({ metric, metric_uuid, reload }) {
    const dataModel = useContext(DataModel)
    const scale = getMetricScale(metric, dataModel)
    const metricType = dataModel.metrics[metric.type];
    const scale_options = metric_scale_options(metricType.scales || ["count"], dataModel);
    const labelId = `scale-${metric_uuid}`
    return (
        <SingleChoiceInput
            aria-labelledby={labelId}
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label={<label id={labelId}>Metric scale</label>}
            options={scale_options}
            placeholder={metricType.default_scale || "Count"}
            set_value={(value) => set_metric_attribute(metric_uuid, "scale", value, reload)}
            value={scale}
        />
    )
}
Scale.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
}

function Direction({ metric, metric_uuid, reload }) {
    const dataModel = useContext(DataModel)
    const scale = getMetricScale(metric, dataModel)
    const metricType = dataModel.metrics[metric.type];
    const metricUnitWithoutPercentage = metric.unit || metricType.unit;
    const metricUnit = `${scale === "percentage" ? "% " : ""}${metricUnitWithoutPercentage}`;
    const fewer = { count: `Fewer ${metricUnit}`, percentage: `A lower percentage of ${metricUnitWithoutPercentage}`, version_number: "A lower version number" }[scale];
    const more = { count: `More ${metricUnit}`, percentage: `A higher percentage of ${metricUnitWithoutPercentage}`, version_number: "A higher version number" }[scale];
    const metricDirection = getMetricDirection(metric, dataModel) ?? "<"
    const labelId = `direction-${metric_uuid}`
    return (
        <SingleChoiceInput
            aria-labelledby={labelId}
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label={<label id={labelId}>Metric direction</label>}
            options={[
                { key: "0", text: `${fewer} is better`, value: "<" },
                { key: "1", text: `${more} is better`, value: ">" }]}
            set_value={(value) => set_metric_attribute(metric_uuid, "direction", value, reload)}
            value={metricDirection}
        />
    )
}
Direction.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
}

function Unit({ metric, metric_uuid, reload }) {
    const dataModel = useContext(DataModel)
    const metricType = dataModel.metrics[metric.type];
    const labelId = `unit-${metric_uuid}`
    return (
        <StringInput
            aria-labelledby={labelId}
            label={<label id={labelId}>Metric unit</label>}
            placeholder={metricType.unit}
            prefix={formatMetricScale(metric, dataModel)}
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            set_value={(value) => set_metric_attribute(metric_uuid, "unit", value, reload)}
            value={metric.unit ?? ""}
        />
    )
}
Unit.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
}

function EvaluateTargets({ metric, metric_uuid, reload }) {
    const help = "Turning off evaluation of the metric targets makes this an informative metric. Informative metrics do not turn red, green, or yellow, and can't have accepted technical debt."
    const labelId = `evaluate-targets-label-${metric_uuid}`
    return (
        <SingleChoiceInput
            aria-labelledby={labelId}
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label={<LabelWithHelp labelId={labelId} label="Evaluate metric targets?" help={help} />}
            value={metric.evaluate_targets ?? true}
            options={[
                { key: true, text: "Yes", value: true },
                { key: false, text: "No", value: false }]}
            set_value={(value) => set_metric_attribute(metric_uuid, "evaluate_targets", value, reload)}
        />
    )
}
EvaluateTargets.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
}

export function MetricConfigurationParameters({ metric, metric_uuid, reload, report, subject }) {
    const dataModel = useContext(DataModel)
    const metricScale = getMetricScale(metric, dataModel);
    return (
        <Grid stackable columns={3}>
            <Grid.Row>
                <Grid.Column>
                    <MetricType subjectType={subject.type} metricType={metric.type} metric_uuid={metric_uuid} reload={reload} />
                </Grid.Column>
                <Grid.Column>
                    <MetricName metric={metric} metric_uuid={metric_uuid} reload={reload} />
                </Grid.Column>
                <Grid.Column>
                    <Tags metric={metric} metric_uuid={metric_uuid} reload={reload} report={report} />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row>
                <Grid.Column>
                    <Scale metric={metric} metric_uuid={metric_uuid} reload={reload} />
                </Grid.Column>
                <Grid.Column>
                    <Direction metric={metric} metric_uuid={metric_uuid} reload={reload} />
                </Grid.Column>
                {metricScale !== "version_number" &&
                    <Grid.Column>
                        <Unit metric={metric} metric_uuid={metric_uuid} reload={reload} />
                    </Grid.Column>}
            </Grid.Row>
            <Grid.Row>
                <Grid.Column>
                    <EvaluateTargets metric={metric} metric_uuid={metric_uuid} reload={reload} />
                </Grid.Column>
                <Grid.Column>
                    <Target label="Metric target" labelPosition='top center' target_type="target" metric={metric} metric_uuid={metric_uuid} reload={reload} />
                </Grid.Column>
                <Grid.Column>
                    <Target label="Metric near target" labelPosition='top right' target_type="near_target" metric={metric} metric_uuid={metric_uuid} reload={reload} />
                </Grid.Column>
            </Grid.Row>
        </Grid>
    );
}
MetricConfigurationParameters.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
    report: reportPropType,
    subject: subjectPropType,
}
