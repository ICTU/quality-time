import { Autocomplete, TextField } from "@mui/material"
import { arrayOf, bool, element, func, object, oneOfType, string } from "prop-types"

import { stringsPropType } from "../sharedPropTypes"

export function MultipleChoiceField({
    disabled,
    freeSolo,
    helperText,
    label,
    onChange,
    onInputChange,
    options,
    placeholder,
    startAdornment,
    value,
}) {
    return (
        <Autocomplete
            value={value}
            disabled={disabled}
            filterOptions={(x) => x} // Disable built-in filtering
            filterSelectedOptions
            freeSolo={freeSolo} // Allow additional options
            fullWidth
            multiple
            options={options}
            onChange={(_event, value) => onChange(value.map((value) => value?.id ?? value))}
            onInputChange={onInputChange}
            renderInput={(params) => {
                return (
                    <TextField
                        {...params}
                        helperText={helperText}
                        label={label}
                        placeholder={value.length === 0 ? placeholder : ""}
                        slotProps={{
                            input: {
                                ...params.InputProps,
                                startAdornment: (
                                    <>
                                        {startAdornment}
                                        {params.InputProps.startAdornment}
                                    </>
                                ),
                            },
                        }}
                    />
                )
            }}
        />
    )
}
MultipleChoiceField.propTypes = {
    disabled: bool,
    freeSolo: bool,
    helperText: string,
    label: string,
    onChange: func,
    onInputChange: func,
    options: oneOfType([stringsPropType, arrayOf(object)]),
    placeholder: string,
    startAdornment: element,
    value: stringsPropType,
}
