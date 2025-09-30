import { MenuItem, Stack, Typography } from "@mui/material"
import Grid from "@mui/material/Grid"
import { func, string } from "prop-types"
import { useContext } from "react"

import { setMetricAttribute } from "../api/metric"
import { DataModel } from "../context/DataModel"
import { accessGranted, EDIT_REPORT_PERMISSION, Permissions } from "../context/Permissions"
import { MultipleChoiceField } from "../fields/MultipleChoiceField"
import { TextField } from "../fields/TextField"
import { metricPropType, reportPropType, subjectPropType } from "../sharedPropTypes"
import { formatMetricScale, getMetricDirection, getMetricScale, getMetricTags, getReportTags } from "../utils"
import { MetricType } from "./MetricType"
import { Target } from "./Target"
import { TargetVisualiser } from "./TargetVisualiser"

function metricScaleOptions(metricScales, dataModel) {
    let scaleOptions = []
    metricScales.forEach((scale) => {
        let scaleName = dataModel.scales ? dataModel.scales[scale].name : "Count"
        let scaleDescription = dataModel.scales ? dataModel.scales[scale].description : ""
        scaleOptions.push({
            content: (
                <Stack direction="column" sx={{ whiteSpace: "normal" }}>
                    {scaleName}
                    <Typography variant="body2">{scaleDescription}</Typography>
                </Stack>
            ),
            key: scale,
            text: scaleName,
            value: scale,
        })
    })
    return scaleOptions
}

function MetricName({ metric, metricUuid, reload }) {
    const dataModel = useContext(DataModel)
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const metricType = dataModel.metrics[metric.type]
    return (
        <TextField
            disabled={disabled}
            label="Metric name"
            placeholder={metricType.name}
            onChange={(value) => setMetricAttribute(metricUuid, "name", value, reload)}
            value={metric.name}
        />
    )
}
MetricName.propTypes = {
    metric: metricPropType,
    metricUuid: string,
    reload: func,
}

function MetricSecondaryName({ metric, metricUuid, reload }) {
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    return (
        <TextField
            disabled={disabled}
            label="Metric secondary name"
            onChange={(value) => setMetricAttribute(metricUuid, "secondary_name", value, reload)}
            value={metric.secondary_name}
        />
    )
}
MetricSecondaryName.propTypes = {
    metric: metricPropType,
    metricUuid: string,
    reload: func,
}

function Tags({ metric, metricUuid, reload, report }) {
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const tags = getReportTags(report)
    return (
        <MultipleChoiceField
            disabled={disabled}
            freeSolo
            label="Metric tags"
            options={tags}
            onChange={(value) => setMetricAttribute(metricUuid, "tags", value, reload)}
            value={getMetricTags(metric)}
        />
    )
}
Tags.propTypes = {
    metric: metricPropType,
    metricUuid: string,
    reload: func,
    report: reportPropType,
}

function Scale({ metric, metricUuid, reload }) {
    const dataModel = useContext(DataModel)
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const scale = getMetricScale(metric, dataModel)
    const metricType = dataModel.metrics[metric.type]
    const scaleOptions = metricScaleOptions(metricType.scales || ["count"], dataModel)
    return (
        <TextField
            disabled={disabled}
            label="Metric scale"
            onChange={(value) => setMetricAttribute(metricUuid, "scale", value, reload)}
            placeholder={metricType.default_scale || "Count"}
            select
            value={scale}
        >
            {scaleOptions.map((option) => (
                <MenuItem key={option.key} value={option.value}>
                    {option.content}
                </MenuItem>
            ))}
        </TextField>
    )
}
Scale.propTypes = {
    metric: metricPropType,
    metricUuid: string,
    reload: func,
}

function Direction({ metric, metricUuid, reload }) {
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
            onChange={(value) => setMetricAttribute(metricUuid, "direction", value, reload)}
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
    metricUuid: string,
    reload: func,
}

function Unit({ metric, metricUuid, reload }) {
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
            onChange={(value) => setMetricAttribute(metricUuid, "unit", value, reload)}
            value={metric.unit}
        />
    )
}
Unit.propTypes = {
    metric: metricPropType,
    metricUuid: string,
    reload: func,
}

function EvaluateTargets({ metric, metricUuid, reload }) {
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, [EDIT_REPORT_PERMISSION])
    const help =
        "Turning off evaluation of the metric targets makes this an informative metric. Informative metrics do not turn red, green, or yellow, and can't have accepted technical debt."
    return (
        <TextField
            disabled={disabled}
            helperText={help}
            label="Evaluate metric targets?"
            onChange={(value) => setMetricAttribute(metricUuid, "evaluate_targets", value, reload)}
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
    metricUuid: string,
    reload: func,
}

export function MetricConfigurationParameters({ metric, metricUuid, reload, report, subject }) {
    const dataModel = useContext(DataModel)
    const metricScale = getMetricScale(metric, dataModel)
    const commonParameterProps = { metric: metric, metricUuid: metricUuid, reload: reload }
    return (
        <Grid container spacing={{ xs: 1, sm: 2, md: 3 }} columns={{ xs: 1, sm: 3, md: 3 }}>
            <Grid size={1}>
                <MetricType
                    subjectType={subject.type}
                    metricType={metric.type}
                    metricUuid={metricUuid}
                    reload={reload}
                />
            </Grid>
            <Grid size={1}>
                <Stack spacing={{ xs: 1, sm: 1, md: 1 }}>
                    <MetricName {...commonParameterProps} />
                    <MetricSecondaryName {...commonParameterProps} />
                </Stack>
            </Grid>
            <Grid size={1}>
                <Tags report={report} {...commonParameterProps} />
            </Grid>
            <Grid size={1}>
                <Scale {...commonParameterProps} />
            </Grid>
            <Grid size={1}>
                <Direction {...commonParameterProps} />
            </Grid>
            <Grid size={1}>{metricScale !== "version_number" && <Unit {...commonParameterProps} />}</Grid>
            <Grid size={1}>
                <EvaluateTargets {...commonParameterProps} />
            </Grid>
            <Grid size={1}>
                <Target targetType="target" {...commonParameterProps} />
            </Grid>
            <Grid size={1}>
                <Target targetType="near_target" {...commonParameterProps} />
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
    metricUuid: string,
    reload: func,
    report: reportPropType,
    subject: subjectPropType,
}
