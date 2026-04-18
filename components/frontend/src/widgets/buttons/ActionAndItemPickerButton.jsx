import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown"
import { Button, MenuItem, MenuList, Popover, TextField, Tooltip, Typography } from "@mui/material"
import { element, func, string } from "prop-types"
import { useState } from "react"

import { ItemBreadcrumb } from "../ItemBreadcrumb"

export function ActionAndItemPickerButton({ action, itemType, onChange, getOptions, icon }) {
    const [anchorEl, setAnchorEl] = useState()
    const [query, setQuery] = useState("") // Search query to filter items
    const handleMenu = (event) => setAnchorEl(event.currentTarget)
    const onClick = (value) => {
        onChange(value)
        setAnchorEl(null)
    }

    const options = getOptions().filter((option) => option.text.toLowerCase().includes(query.toLowerCase()))

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
                <Button aria-controls={anchorEl ? "action-menu" : null} onClick={handleMenu} variant="outlined">
                    {icon}&nbsp;{`${action} ${itemType} `}
                    <ArrowDropDownIcon />
                </Button>
            </Tooltip>
            <Popover id="dropdown-menu" anchorEl={anchorEl} onClose={() => setAnchorEl(null)} open={Boolean(anchorEl)}>
                <TextField
                    autoFocus
                    fullWidth
                    label={`Filter ${itemType}s`}
                    onChange={(event) => setQuery(event.target.value)}
                    value={query}
                    variant="outlined"
                    sx={{ ml: "10px", mt: "10px", pr: "20px" }}
                    type="search"
                />
                <MenuList sx={{ height: "30vh", width: "50vw" }}>
                    <MenuItem disabled divider>
                        <Typography variant="button">
                            <ItemBreadcrumb {...breadcrumbProps} />
                        </Typography>
                    </MenuItem>
                    {options.map((option) => (
                        <MenuItem key={option.key} onClick={() => onClick(option.value)}>
                            {option.content}
                        </MenuItem>
                    ))}
                </MenuList>
            </Popover>
        </>
    )
}
ActionAndItemPickerButton.propTypes = {
    action: string,
    itemType: string,
    onChange: func,
    getOptions: func,
    icon: element,
}
