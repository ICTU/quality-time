import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown"
import {
    Button,
    Checkbox,
    FormControlLabel,
    FormGroup,
    MenuItem,
    MenuList,
    Popover,
    TextField,
    Tooltip,
    Typography,
} from "@mui/material"
import { array, arrayOf, bool, func, string } from "prop-types"
import { useState } from "react"

import { AddItemIcon } from "../icons"

function FilterCheckbox({ label, filter, setFilter }) {
    return (
        <FormControlLabel
            control={
                <Checkbox
                    checked={filter}
                    inputProps={{ "aria-label": "controlled" }}
                    onChange={() => setFilter(!filter)}
                />
            }
            label={label}
        />
    )
}
FilterCheckbox.propTypes = {
    label: string,
    filter: bool,
    setFilter: func,
}

function FilterCheckboxes({
    itemType,
    allowHidingUnsupportedItems,
    showUnsupportedItems,
    setShowUnsupportedItems,
    allowHidingUsedItems,
    hideUsedItems,
    setHideUsedItems,
}) {
    if (!allowHidingUnsupportedItems && !allowHidingUsedItems) {
        return null
    }
    return (
        <FormGroup row sx={{ ml: "10px" }}>
            {allowHidingUnsupportedItems && (
                <FilterCheckbox
                    label={`Select from all ${itemType} types`}
                    filter={showUnsupportedItems}
                    setFilter={setShowUnsupportedItems}
                />
            )}
            {allowHidingUsedItems && (
                <FilterCheckbox
                    label={`Hide ${itemType} types already used`}
                    filter={hideUsedItems}
                    setFilter={setHideUsedItems}
                />
            )}
        </FormGroup>
    )
}
FilterCheckboxes.propTypes = {
    itemType: string,
    allowHidingUnsupportedItems: bool,
    showUnsupportedItems: bool,
    setShowUnsupportedItems: func,
    allowHidingUsedItems: bool,
    hideUsedItems: bool,
    setHideUsedItems: func,
}

export function AddDropdownButton({ itemSubtypes, itemType, onClick, allItemSubtypes, usedItemSubtypeKeys, sort }) {
    const [anchorEl, setAnchorEl] = useState()
    const handleMenu = (event) => setAnchorEl(event.currentTarget)
    const onClickMenuItem = (value) => {
        onClick(value)
        setAnchorEl(null)
    }
    const [query, setQuery] = useState("") // Search query to filter item subtypes
    const [showUnsupportedItems, setShowUnsupportedItems] = useState(false) // Show only supported itemSubTypes or also unsupported itemSubTypes?
    const [hideUsedItems, setHideUsedItems] = useState(false) // Hide itemSubTypes already used?
    let items = showUnsupportedItems ? allItemSubtypes : itemSubtypes
    if (hideUsedItems) {
        items = items.filter((item) => !usedItemSubtypeKeys.includes(item.key))
    }
    const options = items.filter((itemSubtype) => itemSubtype.text.toLowerCase().includes(query.toLowerCase()))
    // Unless specified not to, sort the options:
    if (sort !== false) {
        options.sort((a, b) => a.text.localeCompare(b.text))
    }
    return (
        <>
            <Tooltip title={`Add a new ${itemType} here`} placement="top">
                <Button aria-describedby="dropdown-menu" onClick={handleMenu} variant="outlined">
                    <AddItemIcon /> {`Add ${itemType} `} <ArrowDropDownIcon />
                </Button>
            </Tooltip>
            <Popover id="dropdown-menu" anchorEl={anchorEl} onClose={() => setAnchorEl(null)} open={Boolean(anchorEl)}>
                <TextField
                    fullWidth
                    label={`Filter ${itemType} types`}
                    onChange={(event) => setQuery(event.target.value)}
                    value={query}
                    variant="outlined"
                    sx={{ ml: "10px", mt: "10px", pr: "20px" }}
                    type="search"
                />
                <FilterCheckboxes
                    itemType={itemType}
                    allowHidingUnsupportedItems={allItemSubtypes?.length > 0}
                    showUnsupportedItems={showUnsupportedItems}
                    setShowUnsupportedItems={setShowUnsupportedItems}
                    allowHidingUsedItems={usedItemSubtypeKeys?.length > 0}
                    hideUsedItems={hideUsedItems}
                    setHideUsedItems={setHideUsedItems}
                />
                <MenuList sx={{ height: "30vh", width: "50vw" }}>
                    <MenuItem disabled divider>
                        <Typography variant="button">{`Available ${itemType} types`}</Typography>
                    </MenuItem>
                    {options.map((option) => (
                        <MenuItem
                            key={option.key}
                            onClick={() => onClickMenuItem(option.value)}
                            sx={{ whiteSpace: "wrap" }}
                        >
                            {option.content}
                        </MenuItem>
                    ))}
                </MenuList>
            </Popover>
        </>
    )
}
AddDropdownButton.propTypes = {
    allItemSubtypes: array,
    itemSubtypes: array,
    itemType: string,
    onClick: func,
    sort: bool,
    usedItemSubtypeKeys: arrayOf(string),
}
