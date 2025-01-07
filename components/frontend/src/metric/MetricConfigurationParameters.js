import { MenuItem, Stack, Typography } from "@mui/material"
import Grid from "@mui/material/Grid2"
import { func, string } from "prop-types"
import { useContext } from "react"

import { set_metric_attribute } from "../api/metric"
import { DataModel } from "../context/DataModel"
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { MultipleChoiceField } from "../fields/MultipleChoiceField"
import { TextField } from "../fields/TextField"
import { metricPropType, reportPropType, subjectPropType } from "../sharedPropTypes"
import { formatMetricScale, getMetricDirection, getMetricScale, getMetricTags, getReportTags } from "../utils"
import { MetricType } from "./MetricType"
import { Target } from "./Target"
import { TargetVisualiser } from "./TargetVisualiser"

function metric_scale_options(metric_scales, dataModel) {
    let scale_options = []
    metric_scales.forEach((scale) => {
        let scale_name = dataModel.scales ? dataModel.scales[scale].name : "Count"
        let scale_description = dataModel.scales ? dataModel.scales[scale].description : ""
        scale_options.push({
            content: (
                <Stack direction="column" sx={{ whiteSpace: "normal" }}>
                    {scale_name}
                    <Typography variant="body2">{scale_description}</Typography>
                </Stack>
            ),
            key: scale,
            text: scale_name,
            value: scale,
        })
    })
    return scale_options
}

function MetricName({ metric, metric_uuid, reload }) {
    const dataModel = useContext(DataModel)
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const metricType = dataModel.metrics[metric.type]
    return (
        <TextField
            disabled={disabled}
            label="Metric name"
            placeholder={metricType.name}
            onChange={(value) => set_metric_attribute(metric_uuid, "name", value, reload)}
            value={metric.name}
        />
    )
}
MetricName.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
}

function Tags({ metric, metric_uuid, reload, report }) {
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const tags = getReportTags(report)
    return (
        <MultipleChoiceField
            disabled={disabled}
            freeSolo
            label="Metric tags"
            options={tags}
            onChange={(value) => set_metric_attribute(metric_uuid, "tags", value, reload)}
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
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const scale = getMetricScale(metric, dataModel)
    const metricType = dataModel.metrics[metric.type]
    const scale_options = metric_scale_options(metricType.scales || ["count"], dataModel)
    return (
        <TextField
            disabled={disabled}
            label="Metric scale"
            onChange={(value) => set_metric_attribute(metric_uuid, "scale", value, reload)}
            placeholder={metricType.default_scale || "Count"}
            select
            value={scale}
        >
            {scale_options.map((option) => (
                <MenuItem key={option.key} value={option.value}>
                    {option.content}
                </MenuItem>
            ))}
        </TextField>
    )
}
Scale.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
}

function Direction({ metric, metric_uuid, reload }) {
    const dataModel = useContext(DataModel)
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const scale = getMetricScale(metric, dataModel)
    const metricType = dataModel.metrics[metric.type]
    const metricUnitWithoutPercentage = metric.unit || metricType.unit
    const metricUnit = `${scale === "percentage" ? "% " : ""}${metricUnitWithoutPercentage}`
    const fewer = {
        count: `Fewer ${metricUnit}`,
        percentage: `A lower percentage of ${metricUnitWithoutPercentage}`,
        version_number: "A lower version number",
    }[scale]
    const more = {
        count: `More ${metricUnit}`,
        percentage: `A higher percentage of ${metricUnitWithoutPercentage}`,
        version_number: "A higher version number",
    }[scale]
    return (
        <TextField
            disabled={disabled}
            label="Metric direction"
            onChange={(value) => set_metric_attribute(metric_uuid, "direction", value, reload)}
            select
            value={getMetricDirection(metric, dataModel) ?? "<"}
        >
            <MenuItem key="0" value="<">
                {`${fewer} is better`}
            </MenuItem>
            <MenuItem key="1" value=">">
                {`${more} is better`}
            </MenuItem>
        </TextField>
    )
}
Direction.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
}

function Unit({ metric, metric_uuid, reload }) {
    const dataModel = useContext(DataModel)
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const metricType = dataModel.metrics[metric.type]
    return (
        <TextField
            disabled={disabled}
            label="Metric unit"
            placeholder={metricType.unit}
            startAdornment={formatMetricScale(metric, dataModel)}
            onChange={(value) => set_metric_attribute(metric_uuid, "unit", value, reload)}
            value={metric.unit}
        />
    )
}
Unit.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
}

function EvaluateTargets({ metric, metric_uuid, reload }) {
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const help =
        "Turning off evaluation of the metric targets makes this an informative metric. Informative metrics do not turn red, green, or yellow, and can't have accepted technical debt."
    return (
        <TextField
            disabled={disabled}
            helperText={help}
            label="Evaluate metric targets?"
            onChange={(value) => set_metric_attribute(metric_uuid, "evaluate_targets", value, reload)}
            select
            value={metric.evaluate_targets ?? true}
        >
            <MenuItem key={true} value={true}>
                Yes
            </MenuItem>
            <MenuItem key={false} value={false}>
                No
            </MenuItem>
        </TextField>
    )
}
EvaluateTargets.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
}

export function MetricConfigurationParameters({ metric, metric_uuid, reload, report, subject }) {
    const dataModel = useContext(DataModel)
    const metricScale = getMetricScale(metric, dataModel)
    return (
        <Grid container spacing={{ xs: 1, sm: 2, md: 3 }} columns={{ xs: 1, sm: 3, md: 3 }}>
            <Grid size={1}>
                <MetricType
                    subjectType={subject.type}
                    metricType={metric.type}
                    metric_uuid={metric_uuid}
                    reload={reload}
                />
            </Grid>
            <Grid size={1}>
                <MetricName metric={metric} metric_uuid={metric_uuid} reload={reload} />
            </Grid>
            <Grid size={1}>
                <Tags metric={metric} metric_uuid={metric_uuid} reload={reload} report={report} />
            </Grid>
            <Grid size={1}>
                <Scale metric={metric} metric_uuid={metric_uuid} reload={reload} />
            </Grid>
            <Grid size={1}>
                <Direction metric={metric} metric_uuid={metric_uuid} reload={reload} />
            </Grid>
            <Grid size={1}>
                {metricScale !== "version_number" && <Unit metric={metric} metric_uuid={metric_uuid} reload={reload} />}
            </Grid>
            <Grid size={1}>
                <EvaluateTargets metric={metric} metric_uuid={metric_uuid} reload={reload} />
            </Grid>
            <Grid size={1}>
                <Target target_type="target" metric={metric} metric_uuid={metric_uuid} reload={reload} />
            </Grid>
            <Grid size={1}>
                <Target target_type="near_target" metric={metric} metric_uuid={metric_uuid} reload={reload} />
            </Grid>
            <Grid size={3}>
                <Stack spacing={1}>
                    <Typography variant="h4">How targets are evaluated</Typography>
                    <TargetVisualiser metric={metric} />
                </Stack>
            </Grid>
        </Grid>
    )
}
MetricConfigurationParameters.propTypes = {
    metric: metricPropType,
    metric_uuid: string,
    reload: func,
    report: reportPropType,
    subject: subjectPropType,
}
