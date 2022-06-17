import React, { useContext, useState } from 'react';
import { Grid, Header } from 'semantic-ui-react';
import { Icon, Popup } from '../semantic_ui_react_wrappers';
import { get_report_issue_tracker_suggestions } from '../api/report';
import { MultipleChoiceInput } from '../fields/MultipleChoiceInput';
import { StringInput } from '../fields/StringInput';
import { SingleChoiceInput } from '../fields/SingleChoiceInput';
import { Comment } from '../fields/Comment';
import { set_metric_attribute } from '../api/metric';
import { DateInput } from '../fields/DateInput';
import { HyperLink } from '../widgets/HyperLink';
import { ErrorMessage } from '../errorMessage';
import { DataModel } from '../context/DataModel';
import { EDIT_REPORT_PERMISSION } from '../context/Permissions';
import { dropdownOptions, getMetricDirection, get_metric_issue_ids, getMetricScale, get_metric_tags } from '../utils';
import { MetricType } from './MetricType';
import { Target } from './Target';

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

function MetricName({ metric, metricType, metric_uuid, reload }) {
    return (
        <StringInput
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            id="metric-name"
            label="Metric name"
            placeholder={metricType.name}
            set_value={(value) => set_metric_attribute(metric_uuid, "name", value, reload)}
            value={metric.name ?? ""}
        />
    )
}

function Tags({ metric, metric_uuid, reload, report }) {
    const tags = Object.keys(report.summary_by_tag || []);
    return (
        <MultipleChoiceInput
            allowAdditions
            label="Tags"
            options={dropdownOptions(tags)}
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            set_value={(value) => set_metric_attribute(metric_uuid, "tags", value, reload)}
            value={get_metric_tags(metric)}
        />
    )
}

function Scale({ metricType, metric_scale, metric_uuid, reload }) {
    const dataModel = useContext(DataModel)
    const scale_options = metric_scale_options(metricType.scales || ["count"], dataModel);
    return (
        <SingleChoiceInput
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label="Metric scale"
            options={scale_options}
            placeholder={metricType.default_scale || "Count"}
            set_value={(value) => set_metric_attribute(metric_uuid, "scale", value, reload)}
            value={metric_scale}
        />
    )
}

function Direction({ metric, metric_scale, metric_uuid, metricType, reload }) {
    const dataModel = useContext(DataModel)
    const metricUnitWithoutPercentage = metric.unit || metricType.unit;
    const metricUnit = `${metric_scale === "percentage" ? "% " : ""}${metricUnitWithoutPercentage}`;
    const fewer = { count: `Fewer ${metricUnit}`, percentage: `A lower percentage of ${metricUnitWithoutPercentage}`, version_number: "A lower version number" }[metric_scale];
    const more = { count: `More ${metricUnit}`, percentage: `A higher percentage of ${metricUnitWithoutPercentage}`, version_number: "A higher version number" }[metric_scale];
    const metricDirection = getMetricDirection(metric, dataModel) ?? "<"
    return (
        <SingleChoiceInput
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label="Metric direction"
            options={[
                { key: "0", text: `${fewer} is better`, value: "<" },
                { key: "1", text: `${more} is better`, value: ">" }]}
            set_value={(value) => set_metric_attribute(metric_uuid, "direction", value, reload)}
            value={metricDirection}
        />
    )
}

function Unit({ metric, metric_scale, metric_uuid, metricType, reload }) {
    return (
        <StringInput
            id="metric-unit"
            label="Metric unit"
            placeholder={metricType.unit}
            prefix={metric_scale === "percentage" ? "%" : ""}
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            set_value={(value) => set_metric_attribute(metric_uuid, "unit", value, reload)}
            value={metric.unit ?? ""}
        />
    )
}

function EvaluateTargets({ metric, metric_uuid, reload }) {
    const help = "Turning off evaluation of the metric targets makes this an informative metric. Informative metrics do not turn red, green, or yellow, and can't have accepted technical debt."
    const labelId = `evaluate-targets-label-${metric_uuid}`
    return (
        <SingleChoiceInput
            aria-labelledby={labelId}
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label={<label id={labelId}>Evaluate metric targets? <Popup on={['hover', 'focus']} content={help} trigger={<Icon tabIndex="0" name="help circle" />} /></label>}
            value={metric.evaluate_targets ?? true}
            options={[
                { key: true, text: "Yes", value: true },
                { key: false, text: "No", value: false }]}
            set_value={(value) => set_metric_attribute(metric_uuid, "evaluate_targets", value, reload)}
        />
    )
}

function AcceptTechnicalDebt({ metric, metric_uuid, reload }) {
    return (
        <SingleChoiceInput
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label={<label>Accept technical debt? <HyperLink url="https://en.wikipedia.org/wiki/Technical_debt"><Icon tabIndex="0" name="help circle" link /></HyperLink></label>}
            value={metric.accept_debt || false}
            options={[
                { key: true, text: "Yes", value: true },
                { key: false, text: "No", value: false }]}
            set_value={(value) => set_metric_attribute(metric_uuid, "accept_debt", value, reload)}
        />
    )
}

function TechnicalDebtEndDate({ metric, metric_uuid, reload }) {
    return (
        <DateInput
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label="Technical debt end date"
            placeholder="YYYY-MM-DD"
            set_value={(value) => set_metric_attribute(metric_uuid, "debt_end_date", value, reload)}
            value={metric.debt_end_date ?? ""}
        />
    )
}

function IssueIdentifiers({ issue_tracker_instruction, metric, metric_uuid, reload, report }) {
    const issueStatusHelp = "Identifiers of issues in the configured issue tracker that track the progress of fixing this metric." + (report.issue_tracker ? "" : ` ${issue_tracker_instruction}`);
    const [suggestions, setSuggestions] = useState([]);
    const labelId = `issue-identifiers-label-${metric_uuid}`
    return (
        <MultipleChoiceInput
            aria-labelledby={labelId}
            allowAdditions
            onSearchChange={(query) => {
                if (query) {
                    get_report_issue_tracker_suggestions(report.report_uuid, query).then((suggestionsResponse) => {
                        const suggestionOptions = suggestionsResponse.suggestions.map((s) => ({ key: s.key, text: `${s.key}: ${s.text}`, value: s.key }))
                        setSuggestions(suggestionOptions)
                    })
                } else {
                    setSuggestions([])
                }
            }}
            requiredPermissions={[EDIT_REPORT_PERMISSION]}
            label={<label id={labelId}>Issue identifiers <Popup on={['hover', 'focus']} content={issueStatusHelp} trigger={<Icon tabIndex="0" name="help circle" />} /></label>}
            options={suggestions}
            set_value={(value) => set_metric_attribute(metric_uuid, "issue_ids", value, reload)}
            value={get_metric_issue_ids(metric)}
        />
    )
}

export function MetricParameters({ report, subject, metric, metric_uuid, reload }) {
    const dataModel = useContext(DataModel)
    const metricType = dataModel.metrics[metric.type];
    const metric_scale = getMetricScale(metric, dataModel);
    const issue_tracker_instruction = "Please configure an issue tracker by expanding the report title, selecting the 'Issue tracker' tab, and configuring an issue tracker."
    return (
        <Grid stackable columns={3}>
            <Grid.Row>
                <Grid.Column>
                    <MetricType subjectType={subject.type} metricType={metric.type} metric_uuid={metric_uuid} reload={reload} />
                </Grid.Column>
                <Grid.Column>
                    <MetricName metric={metric} metricType={metricType} metric_uuid={metric_uuid} reload={reload} />
                </Grid.Column>
                <Grid.Column>
                    <Tags metric={metric} metric_uuid={metric_uuid} reload={reload} report={report} />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row>
                <Grid.Column>
                    <Scale metricType={metricType} metric_scale={metric_scale} metric_uuid={metric_uuid} reload={reload} />
                </Grid.Column>
                <Grid.Column>
                    <Direction metric={metric} metric_scale={metric_scale} metric_uuid={metric_uuid} metricType={metricType} reload={reload} />
                </Grid.Column>
                {metric_scale !== "version_number" &&
                    <Grid.Column>
                        <Unit metric={metric} metric_scale={metric_scale} metric_uuid={metric_uuid} metricType={metricType} reload={reload} />
                    </Grid.Column>}
            </Grid.Row>
            <Grid.Row>
                <Grid.Column>
                    <EvaluateTargets metric={metric} metric_uuid={metric_uuid} reload={reload} />
                </Grid.Column>
                <Grid.Column>
                    <Target label="Metric target" target_type="target" metric={metric} metric_uuid={metric_uuid} reload={reload} />
                </Grid.Column>
                <Grid.Column>
                    <Target label="Metric near target" target_type="near_target" metric={metric} metric_uuid={metric_uuid} reload={reload} />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row>
                <Grid.Column>
                    <AcceptTechnicalDebt metric={metric} metric_uuid={metric_uuid} reload={reload} />
                </Grid.Column>
                <Grid.Column>
                    <Target label="Accepted technical debt" target_type="debt_target" metric={metric} metric_uuid={metric_uuid} reload={reload} />
                </Grid.Column>
                <Grid.Column>
                    <TechnicalDebtEndDate metric={metric} metric_uuid={metric_uuid} reload={reload} />
                </Grid.Column>
            </Grid.Row>
            <Grid.Row>
                <Grid.Column width={16}>
                    <IssueIdentifiers issue_tracker_instruction={issue_tracker_instruction} metric={metric} metric_uuid={metric_uuid} reload={reload} report={report} />
                </Grid.Column>
            </Grid.Row>
            {(get_metric_issue_ids(metric).length > 0 && !report?.issue_tracker?.type) &&
                <Grid.Row>
                    <Grid.Column width={16}>
                        <ErrorMessage title="No issue tracker configured" message={issue_tracker_instruction} />
                    </Grid.Column>
                </Grid.Row>
            }
            {(metric.issue_status ?? []).filter((issue_status => issue_status.connection_error)).map((issue_status) =>
                <Grid.Row key={issue_status.issue_id}>
                    <Grid.Column width={16}>
                        <ErrorMessage key={issue_status.issue_id} title={"Connection error while retrieving " + issue_status.issue_id} message={issue_status.connection_error} />
                    </Grid.Column>
                </Grid.Row>
            )}
            {(metric.issue_status ?? []).filter((issue_status => issue_status.parse_error)).map((issue_status) =>
                <Grid.Row key={issue_status.issue_id}>
                    <Grid.Column width={16}>
                        <ErrorMessage key={issue_status.issue_id} title={"Parse error while processing " + issue_status.issue_id} message={issue_status.parse_error} />
                    </Grid.Column>
                </Grid.Row>
            )}
            <Grid.Row>
                <Grid.Column width={16}>
                    <Comment
                        set_value={(value) => set_metric_attribute(metric_uuid, "comment", value, reload)}
                        value={metric.comment}
                    />
                </Grid.Column>
            </Grid.Row>
        </Grid>
    );
}
