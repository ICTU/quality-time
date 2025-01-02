import { MenuItem, Select } from "@mui/material"
import { array, func, string } from "prop-types"

import { labelPropType } from "../sharedPropTypes"

export function LabelWithDropdown({ label, onChange, options, value }) {
    return (
        <label>
            {label}
            <Select
                onChange={(event) => onChange(event.target.value)}
                value={value}
                inputProps={{ sx: { paddingBottom: "2px", paddingTop: "2px" } }}
                sx={{
                    color: options.find((option) => option.value === value).color,
                    marginLeft: "6px",
                }}
            >
                {options.map((option) => (
                    <MenuItem key={option.key} sx={{ color: option.color }} value={option.value}>
                        {option.text}
                    </MenuItem>
                ))}
            </Select>
        </label>
    )
}
LabelWithDropdown.propTypes = {
    label: labelPropType,
    onChange: func,
    options: array,
    value: string,
}
