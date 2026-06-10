import UpdateIcon from "@mui/icons-material/Update"
import { Button, MenuItem, Stack } from "@mui/material"
import { DatePicker } from "@mui/x-date-pickers/DatePicker"
import dayjs from "dayjs"
import relativeTime from "dayjs/plugin/relativeTime"
import { bool, func, number, object, oneOf, oneOfType, shape, string } from "prop-types"
import { useContext } from "react"

import { setSourceParameter } from "../api/source"
import { accessGranted, PermissionsContext } from "../context/Permissions"
import { MultipleChoiceField } from "../fields/MultipleChoiceField"
import { TextField } from "../fields/TextField"
import { datePropType, permissionsPropType, reportPropType, sourcePropType, stringsPropType } from "../sharedPropTypes"
import { dropdownOptions } from "../utils"
import { HyperLink } from "../widgets/HyperLink"

dayjs.extend(relativeTime)

function sources(report) {
    // Return all sources in the report
    const sources = []
    Object.values(report.subjects).forEach((subject) => {
        Object.values(subject.metrics).forEach((metric) => {
            sources.push(...Object.values(metric.sources))
        })
    })
    return sources
}
sources.propTypes = {
    report: reportPropType,
}

function nextDate(calendarDateParameters, previousDate) {
    // Generate the next date based on the previous date and/or the recurrence parameters
    const frequency = Number.parseInt(calendarDateParameters?.["recurrence_frequency"]) || 1
    const unit = calendarDateParameters?.["recurrence_unit"] ?? "day"
    const offset = calendarDateParameters?.["recurrence_offset"] ?? "today"
    const offsetDate = offset === "today" ? new Date() : previousDate
    return dayjs(offsetDate).add(frequency, unit)
}
nextDate.propTypes = {
    calendarDateParameters: shape({
        recurrence_frequency: number,
        recurrence_unit: oneOf(["day", "week", "month", "year"]),
        recurrence_offset: oneOf(["today", "previous date"]),
    }),
    previousDate: datePropType,
}

function collectParameterValues(report, sourceType, parameterKey) {
    // Collect all values in the current report used for this parameter, for this source type
    let values = new Set()
    sources(report).forEach((source) => {
        if (source.type === sourceType && source.parameters) {
            const value = source.parameters[parameterKey]
            if (value) {
                if (Array.isArray(value)) {
                    value.forEach((item) => values.add(item))
                } else {
                    values.add(value)
                }
            }
        }
    })
    return Array.from(values)
}
collectParameterValues.propTypes = {
    report: reportPropType,
    sourceType: string,
    parameterKey: string,
}

export function SourceParameter({
    parameter,
    parameterKey,
    parameterValue,
    reload,
    report,
    requiredPermissions,
    source,
    sourceUuid,
    unit,
    warning,
}) {
    const permissions = useContext(PermissionsContext)
    const disabled = !accessGranted(permissions, requiredPermissions)
    const parameterType = parameter?.type
    const value = parameterValue || parameter?.default_value
    const parameterValues = parameter?.values || []
    let label = parameter?.name
    let helperText = null
    if (parameter?.help_url) {
        helperText = (
            <>
                See <HyperLink url={parameter.help_url}>{parameter.help_url}</HyperLink> for more information.
            </>
        )
    }
    if (parameter?.help) {
        helperText = parameter.help
    }
    if (parameterType === "date" && value) {
        helperText = dayjs(value).fromNow()
    }
    let parameterProps = {
        disabled: disabled,
        helperText: helperText,
        label: label,
        onChange: (value) => {
            setSourceParameter(sourceUuid, parameterKey, value, reload)
        },
        placeholder: parameter?.placeholder || "",
        required: parameter?.mandatory,
    }
    let parameterInput = null
    if (parameterType === "date") {
        parameterInput = (
            <Stack direction="row" spacing={2} sx={{ alignItems: "baseline" }}>
                <DatePicker
                    {...parameterProps}
                    value={value ? dayjs(value) : null}
                    slotProps={{ actionBar: { actions: ["today"] }, textField: { helperText: helperText } }}
                    sx={{ width: "100%" }}
                    timezone="default"
                />
                <Button
                    disabled={disabled || !value || Number.parseInt(source.parameters?.["recurrence_frequency"]) === 0}
                    onClick={() => {
                        setSourceParameter(sourceUuid, parameterKey, nextDate(source.parameters, value), reload)
                    }}
                    startIcon={<UpdateIcon />}
                    variant="outlined"
                >
                    Set next date
                </Button>
            </Stack>
        )
    }
    parameterProps["value"] = value
    if (parameterType === "password") {
        parameterInput = <TextField {...parameterProps} type="password" />
    }
    if (parameterType === "integer") {
        parameterInput = (
            <TextField
                {...parameterProps}
                max={parameter?.max_value || null}
                min={parameter?.min_value || null}
                type="number"
                unit={parameter?.unit || unit}
            />
        )
    }
    if (parameterType === "single_choice") {
        parameterInput = (
            <TextField {...parameterProps} select>
                {dropdownOptions(parameterValues).map((option) => (
                    <MenuItem key={option.key} value={option.value}>
                        {option.text}
                    </MenuItem>
                ))}
            </TextField>
        )
    }
    if (parameterType === "multiple_choice_with_defaults" || parameterType === "multiple_choice_without_defaults") {
        parameterInput = <MultipleChoiceField {...parameterProps} options={parameterValues} />
    }
    if (parameterType === "multiple_choice_with_addition") {
        parameterInput = <MultipleChoiceField {...parameterProps} options={parameterValues} freeSolo />
    }
    parameterProps["options"] = collectParameterValues(report, source.type, parameterKey)
    if (parameterType === "string") {
        parameterInput = <TextField {...parameterProps} />
    }
    if (parameterType === "url") {
        parameterInput = <TextField {...parameterProps} error={warning} />
    }
    return parameterInput
}
SourceParameter.propTypes = {
    parameter: object,
    parameterKey: string,
    parameterValue: oneOfType([string, stringsPropType]),
    reload: func,
    report: reportPropType,
    requiredPermissions: permissionsPropType,
    source: sourcePropType,
    sourceUuid: string,
    unit: string,
    warning: bool,
}
