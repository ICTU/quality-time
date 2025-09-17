import { InputAdornment, TextField as MUITextField } from "@mui/material"
import { bool, element, func, number, oneOfType, string } from "prop-types"
import { useState } from "react"

import { childrenPropType } from "../sharedPropTypes"

export function TextField({
    children,
    disabled,
    endAdornment,
    error,
    helperText,
    id,
    label,
    max,
    multiline,
    onChange,
    placeholder,
    required,
    select,
    startAdornment,
    type,
    value,
}) {
    const [textValue, setTextValue] = useState(value)

    function submitIfChanged() {
        if (textValue !== value) {
            onChange(textValue)
        }
    }

    function onKeyDown(event) {
        if (event.key === "Escape") {
            setTextValue(value)
        }
        if (event.key === "Enter") {
            submitIfChanged()
        }
    }

    const startInputAdornment = startAdornment ? (
        <InputAdornment position="start">{startAdornment}</InputAdornment>
    ) : null
    const endInputAdornment = endAdornment ? (
        <InputAdornment
            position="end"
            sx={{ marginTop: "16px" }} // Adjust margin to vertically align the unit with the input field
        >
            {endAdornment}
        </InputAdornment>
    ) : null
    return (
        <MUITextField
            defaultValue={textValue ?? ""}
            disabled={disabled || (select && children.length === 0)}
            error={error}
            fullWidth
            helperText={helperText}
            id={id}
            label={label}
            maxRows={8}
            minRows={3}
            multiline={multiline}
            onBlur={select ? null : () => submitIfChanged()}
            onChange={select ? (event) => onChange(event.target.value) : (event) => setTextValue(event.target.value)}
            onKeyDown={onKeyDown}
            onWheel={(event) => event.target.blur()} // Prevent scrolling from changing the number value
            placeholder={placeholder}
            required={required}
            select={select && children.length > 0}
            slotProps={{
                input: {
                    endAdornment: endInputAdornment,
                    inputProps: {
                        max: max,
                        min: 0,
                    },
                    startAdornment: startInputAdornment,
                },
            }}
            type={type}
        >
            {children}
        </MUITextField>
    )
}
TextField.propTypes = {
    children: childrenPropType,
    disabled: bool.isRequired,
    endAdornment: oneOfType([element, string]),
    error: bool,
    helperText: oneOfType([element, string]),
    id: string,
    label: oneOfType([element, string]),
    max: number,
    multiline: bool,
    onChange: func,
    placeholder: string,
    required: bool,
    select: bool,
    startAdornment: oneOfType([element, string]),
    type: string,
    value: oneOfType([bool, string]),
}
