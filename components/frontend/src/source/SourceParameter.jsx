import EditIcon from "@mui/icons-material/Edit"
import { FormControl, IconButton, Menu, MenuItem, Typography } from "@mui/material"
import { DatePicker } from "@mui/x-date-pickers/DatePicker"
import dayjs from "dayjs"
import relativeTime from "dayjs/plugin/relativeTime"
import { bool, func, number, oneOfType, string } from "prop-types"
import { useContext, useState } from "react"

import { setSourceParameter } from "../api/source"
import { accessGranted, Permissions } from "../context/Permissions"
import { MultipleChoiceField } from "../fields/MultipleChoiceField"
import { TextField } from "../fields/TextField"
import {
    permissionsPropType,
    popupContentPropType,
    reportPropType,
    sourcePropType,
    stringsPropType,
} from "../sharedPropTypes"
import { dropdownOptions } from "../utils"
import { HyperLink } from "../widgets/HyperLink"

dayjs.extend(relativeTime)

function EditScopeSelect({ editScope, setEditScope }) {
    const scopeOptions = [
        {
            value: "source",
            text: "Apply change to source",
            color: "edit_scope_source",
        },
        {
            value: "metric",
            text: "Apply change to metric",
            color: "edit_scope_metric",
        },
        {
            value: "subject",
            text: "Apply change to subject",
            color: "edit_scope_subject",
        },
        {
            value: "report",
            text: "Apply change to report",
            color: "edit_scope_report",
        },
        {
            value: "reports",
            text: "Apply change to all reports",
            color: "edit_scope_reports",
        },
    ]
    const [anchorEl, setAnchorEl] = useState(null)
    const open = Boolean(anchorEl)
    return (
        <FormControl>
            <IconButton
                aria-controls={open ? "edit-scope-menu" : null}
                aria-expanded={open}
                aria-haspopup="true"
                aria-label="Edit scope"
                color={scopeOptions.find((option) => option.value === editScope).color}
                id="edit-scope-button"
                onClick={(event) => setAnchorEl(event.currentTarget)}
            >
                <EditIcon />
            </IconButton>
            <Menu
                id="edit-scope-menu"
                anchorEl={anchorEl}
                open={open}
                onClose={() => setAnchorEl(null)}
                slotProps={{
                    list: { "aria-labelledby": "edit-scope-button" },
                }}
            >
                {scopeOptions.map((option) => (
                    <MenuItem
                        key={option.value}
                        onClick={() => {
                            setEditScope(option.value)
                            setAnchorEl(null)
                        }}
                        selected={editScope === option.value}
                        value={option.value}
                    >
                        <Typography color={option.color}>{option.text}</Typography>
                    </MenuItem>
                ))}
            </Menu>
        </FormControl>
    )
}
EditScopeSelect.propTypes = {
    editScope: string,
    setEditScope: func,
}

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
    help,
    helpUrl,
    parameterKey,
    parameterType,
    parameterName,
    parameterUnit,
    parameterMin,
    parameterMax,
    parameterValue,
    parameterValues,
    placeholder,
    reload,
    report,
    required,
    requiredPermissions,
    source,
    sourceUuid,
    warning,
}) {
    const [editScope, setEditScope] = useState("source")
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, requiredPermissions)
    let label = parameterName
    let helperText = null
    if (helpUrl) {
        helperText = (
            <>
                See <HyperLink url={helpUrl}>{helpUrl}</HyperLink> for more information.
            </>
        )
    }
    if (help) {
        helperText = help
    }
    if (parameterType === "date" && parameterValue) {
        helperText = dayjs(parameterValue).fromNow()
    }
    let parameterProps = {
        disabled: disabled,
        helperText: helperText,
        label: label,
        onChange: (value) => {
            setSourceParameter(sourceUuid, parameterKey, value, editScope, reload)
            setEditScope("source") // Reset the edit scope of the parameter to source only
        },
        placeholder: placeholder,
        required: required,
    }
    const startAdornment = <EditScopeSelect editScope={editScope} setEditScope={setEditScope} />
    let parameterInput = null
    if (parameterType === "date") {
        parameterInput = (
            <DatePicker
                {...parameterProps}
                defaultValue={parameterValue ? dayjs(parameterValue) : null}
                slotProps={{
                    field: { clearable: true },
                    textField: { helperText: helperText, InputProps: { startAdornment: startAdornment } },
                }}
                sx={{ width: "100%" }}
                timezone="default"
            />
        )
    }
    parameterProps["value"] = parameterValue
    parameterProps["startAdornment"] = startAdornment
    if (parameterType === "password") {
        parameterInput = <TextField {...parameterProps} type="password" />
    }
    if (parameterType === "integer") {
        parameterInput = (
            <TextField
                {...parameterProps}
                max={parameterMax || null}
                min={parameterMin || null}
                type="number"
                unit={parameterUnit}
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
    if (parameterType === "multiple_choice") {
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
    help: popupContentPropType,
    helpUrl: string,
    parameterKey: string,
    parameterType: string,
    parameterName: string,
    parameterUnit: string,
    parameterMin: number,
    parameterMax: number,
    parameterValue: oneOfType([string, stringsPropType]),
    parameterValues: stringsPropType,
    placeholder: string,
    reload: func,
    report: reportPropType,
    required: bool,
    requiredPermissions: permissionsPropType,
    source: sourcePropType,
    sourceUuid: string,
    warning: bool,
}
