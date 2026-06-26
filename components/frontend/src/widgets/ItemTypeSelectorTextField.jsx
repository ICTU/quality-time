import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown"
import { InputAdornment, TextField } from "@mui/material"
import { bool, func, node, string } from "prop-types"

export function ItemTypeSelectorTextField({ handleMenu, disabled, label, helperText, value, startAdornment }) {
    return (
        <TextField
            disabled={disabled}
            fullWidth
            helperText={helperText}
            label={label}
            onClick={disabled ? undefined : handleMenu}
            onKeyDown={
                disabled
                    ? undefined
                    : (event) => {
                          // The input is read-only, so open the popover on the keys a select responds to
                          if (["Enter", " ", "ArrowDown", "ArrowUp"].includes(event.key)) {
                              event.preventDefault()
                              handleMenu(event)
                          }
                      }
            }
            slotProps={{
                input: {
                    readOnly: true,
                    sx: { cursor: disabled ? "default" : "pointer" },
                    startAdornment: startAdornment,
                    endAdornment: (
                        <InputAdornment position="end">
                            <ArrowDropDownIcon />
                        </InputAdornment>
                    ),
                },
            }}
            value={value}
        />
    )
}
ItemTypeSelectorTextField.propTypes = {
    handleMenu: func,
    disabled: bool,
    label: string,
    helperText: node,
    value: string,
    startAdornment: node,
}
