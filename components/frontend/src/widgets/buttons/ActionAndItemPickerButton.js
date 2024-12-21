import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown"
import { Button, Menu, MenuItem, Tooltip, Typography } from "@mui/material"
import { element, func, string } from "prop-types"
import { useState } from "react"

import { ItemBreadcrumb } from "../ItemBreadcrumb"

export function ActionAndItemPickerButton({ action, itemType, onChange, get_options, icon }) {
    const [anchorEl, setAnchorEl] = useState()
    const handleMenu = (event) => setAnchorEl(event.currentTarget)
    const onClick = (value) => {
        onChange(value)
        setAnchorEl(null)
    }

    const breadcrumbProps = { report: "report" }
    if (itemType !== "report") {
        breadcrumbProps.subject = "subject"
        if (itemType !== "subject") {
            breadcrumbProps.metric = "metric"
            if (itemType !== "metric") {
                breadcrumbProps.source = "source"
            }
        }
    }
    return (
        <>
            <Tooltip title={`${action} an existing ${itemType} here`} placement="top">
                <Button aria-controls="action-menu" onClick={handleMenu} variant="outlined">
                    {icon}&nbsp;{`${action} ${itemType} `}
                    <ArrowDropDownIcon />
                </Button>
            </Tooltip>
            <Menu
                id="action-menu"
                anchorEl={anchorEl}
                onClose={() => setAnchorEl(null)}
                open={Boolean(anchorEl)}
                slotProps={{
                    paper: {
                        style: {
                            maxHeight: 250,
                        },
                    },
                }}
            >
                <MenuItem disabled divider>
                    <Typography variant="button">
                        <ItemBreadcrumb size="tiny" {...breadcrumbProps} />
                    </Typography>
                </MenuItem>
                {get_options().map((option) => (
                    <MenuItem key={option.key} onClick={() => onClick(option.value)}>
                        {option.content}
                    </MenuItem>
                ))}
            </Menu>
        </>
    )
}
ActionAndItemPickerButton.propTypes = {
    action: string,
    itemType: string,
    onChange: func,
    get_options: func,
    icon: element,
}
