import EventIcon from "@mui/icons-material/Event"
import { Button, Menu, Tooltip } from "@mui/material"
import { StaticDatePicker } from "@mui/x-date-pickers/StaticDatePicker"
import { func } from "prop-types"
import { useState } from "react"

import { datePropType } from "../../sharedPropTypes"

export function DatePickerButton({ onChange, reportDate }) {
    const [anchorEl, setAnchorEl] = useState()
    const handleMenu = (event) => setAnchorEl(event.currentTarget)
    const handleClose = () => setAnchorEl(null)
    return (
        <Tooltip placement="left" title="Show the report as it was on the selected date">
            <span /* https://mui.com/material-ui/react-tooltip/#disabled-elements */>
                <Button
                    aria-label="Report date"
                    aria-controls="date-picker-button-menu"
                    color="inherit"
                    onClick={handleMenu}
                    startIcon={<EventIcon />}
                    sx={{ height: "100%" }}
                >
                    {reportDate ? reportDate.toDateString() : "today"}
                </Button>
                <Menu id="date-picker-button-menu" anchorEl={anchorEl} onClose={handleClose} open={Boolean(anchorEl)}>
                    <StaticDatePicker
                        disableFuture
                        onChange={(value) => {
                            handleClose()
                            onChange(value)
                        }}
                        slots={{ toolbar: null }}
                        slotProps={{
                            actionBar: {
                                actions: ["today"],
                            },
                        }}
                    />
                </Menu>
            </span>
        </Tooltip>
    )
}
DatePickerButton.propTypes = {
    onChange: func,
    reportDate: datePropType,
}
