import EditIcon from "@mui/icons-material/Edit"
import { FormControl, IconButton, Menu, MenuItem, Typography } from "@mui/material"
import { DatePicker } from "@mui/x-date-pickers/DatePicker"
import dayjs from "dayjs"
import { bool, func, number, oneOfType, string } from "prop-types"
import { useContext, useState } from "react"
import TimeAgo from "react-timeago"

import { set_source_parameter } from "../api/source"
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
                MenuListProps={{ "aria-labelledby": "edit-scope-button" }}
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

function parameterValues(report, sourceType, parameterKey) {
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
parameterValues.propTypes = {
    report: reportPropType,
    sourceType: string,
    parameterKey: string,
}

export function SourceParameter({
    help,
    help_url,
    parameter_key,
    parameter_type,
    parameter_name,
    parameter_unit,
    parameter_min,
    parameter_max,
    parameter_value,
    parameter_values,
    placeholder,
    reload,
    report,
    required,
    requiredPermissions,
    source,
    source_uuid,
    warning,
}) {
    const [editScope, setEditScope] = useState("source")
    const permissions = useContext(Permissions)
    const disabled = !accessGranted(permissions, requiredPermissions)
    let label = parameter_name
    let helperText = null
    if (help_url) {
        helperText = (
            <>
                See <HyperLink url={help_url}>{help_url}</HyperLink> for more information.
            </>
        )
    }
    if (help) {
        helperText = help
    }
    if (parameter_type === "date" && parameter_value) {
        helperText = <TimeAgo date={dayjs(parameter_value)} />
    }
    let parameterProps = {
        disabled: disabled,
        helperText: helperText,
        label: label,
        onChange: (value) => {
            set_source_parameter(source_uuid, parameter_key, value, editScope, reload)
            setEditScope("source") // Reset the edit scope of the parameter to source only
        },
        placeholder: placeholder,
        required: required,
    }
    const startAdornment = <EditScopeSelect editScope={editScope} setEditScope={setEditScope} />
    let parameterInput = null
    if (parameter_type === "date") {
        parameterInput = (
            <DatePicker
                {...parameterProps}
                defaultValue={parameter_value ? dayjs(parameter_value) : null}
                format="YYYY-MM-DD"
                slotProps={{
                    field: { clearable: true },
                    textField: { helperText: helperText, InputProps: { startAdornment: startAdornment } },
                }}
                sx={{ width: "100%" }}
                timezone="default"
            />
        )
    }
    parameterProps["value"] = parameter_value
    parameterProps["startAdornment"] = startAdornment
    if (parameter_type === "password") {
        parameterInput = <TextField {...parameterProps} type="password" />
    }
    if (parameter_type === "integer") {
        parameterInput = (
            <TextField
                {...parameterProps}
                max={parameter_max || null}
                min={parameter_min || null}
                type="number"
                unit={parameter_unit}
            />
        )
    }
    if (parameter_type === "single_choice") {
        parameterInput = (
            <TextField {...parameterProps} select>
                {dropdownOptions(parameter_values).map((option) => (
                    <MenuItem key={option.key} value={option.value}>
                        {option.text}
                    </MenuItem>
                ))}
            </TextField>
        )
    }
    if (parameter_type === "multiple_choice") {
        parameterInput = <MultipleChoiceField {...parameterProps} options={parameter_values} />
    }
    if (parameter_type === "multiple_choice_with_addition") {
        parameterInput = <MultipleChoiceField {...parameterProps} options={parameter_values} freeSolo />
    }
    parameterProps["options"] = parameterValues(report, source.type, parameter_key)
    if (parameter_type === "string") {
        parameterInput = <TextField {...parameterProps} />
    }
    if (parameter_type === "url") {
        parameterInput = <TextField {...parameterProps} error={warning} />
    }
    return parameterInput
}
SourceParameter.propTypes = {
    help: popupContentPropType,
    help_url: string,
    parameter_key: string,
    parameter_type: string,
    parameter_name: string,
    parameter_unit: string,
    parameter_min: number,
    parameter_max: number,
    parameter_value: oneOfType([string, stringsPropType]),
    parameter_values: stringsPropType,
    placeholder: string,
    reload: func,
    report: reportPropType,
    required: bool,
    requiredPermissions: permissionsPropType,
    source: sourcePropType,
    source_uuid: string,
    warning: bool,
}
