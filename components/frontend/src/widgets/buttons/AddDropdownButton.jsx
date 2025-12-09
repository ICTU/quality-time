import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown"
import {
    Button,
    Checkbox,
    FormControlLabel,
    FormGroup,
    MenuItem,
    MenuList,
    Popover,
    Radio,
    RadioGroup,
    TextField,
    Tooltip,
    Typography,
} from "@mui/material"
import { array, arrayOf, bool, func, string } from "prop-types"
import { useState } from "react"

import { AddItemIcon } from "../icons"

function FilterCheckbox({ label, filter, setFilter }) {
    return (
        <FormControlLabel control={<Checkbox checked={filter} onChange={() => setFilter(!filter)} />} label={label} />
    )
}
FilterCheckbox.propTypes = {
    label: string,
    filter: bool,
    setFilter: func,
}

function Filters({
    itemType,
    allowHidingUnsupportedItems,
    showUnsupportedItems,
    setShowUnsupportedItems,
    allowHidingUsedItems,
    hideUsedItems,
    setHideUsedItems,
    hideUsedItemsScope,
    setHideUsedItemsScope,
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
                <>
                    <FilterCheckbox
                        label={`Hide ${itemType} types already used in this:`}
                        filter={hideUsedItems}
                        setFilter={setHideUsedItems}
                    />
                    <RadioGroup
                        row
                        value={hideUsedItemsScope}
                        onChange={(event) => setHideUsedItemsScope(event.target.value)}
                    >
                        <FormControlLabel name="report" value="report" control={<Radio />} label="report" />
                        <FormControlLabel name="subject" value="subject" control={<Radio />} label="subject" />
                    </RadioGroup>
                </>
            )}
        </FormGroup>
    )
}
Filters.propTypes = {
    itemType: string,
    allowHidingUnsupportedItems: bool,
    showUnsupportedItems: bool,
    setShowUnsupportedItems: func,
    allowHidingUsedItems: bool,
    hideUsedItems: bool,
    setHideUsedItems: func,
    hideUsedItemsScope: string,
    setHideUsedItemsScope: func,
}

export function AddDropdownButton({
    itemSubtypes,
    itemType,
    onClick,
    allItemSubtypes,
    usedItemSubtypeKeysInReport,
    usedItemSubtypeKeysInSubject,
    sort,
}) {
    const [anchorEl, setAnchorEl] = useState()
    const handleMenu = (event) => setAnchorEl(event.currentTarget)
    const onClickMenuItem = (value) => {
        onClick(value)
        setAnchorEl(null)
    }
    const [query, setQuery] = useState("") // Search query to filter item subtypes
    const [showUnsupportedItems, setShowUnsupportedItems] = useState(false) // Show only supported itemSubTypes or also unsupported itemSubTypes?
    const [hideUsedItems, setHideUsedItems] = useState(false) // Hide itemSubTypes already used?
    const [hideUsedItemsScope, setHideUsedItemsScope] = useState("report") // Hide itemSubTypes already used in report or subject?
    let items = showUnsupportedItems ? allItemSubtypes : itemSubtypes
    let usedItemKeys = hideUsedItemsScope === "report" ? usedItemSubtypeKeysInReport : usedItemSubtypeKeysInSubject
    if (hideUsedItems) {
        items = items.filter((item) => !usedItemKeys.includes(item.key))
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
                    autoFocus
                    fullWidth
                    label={`Filter ${itemType} types`}
                    onChange={(event) => setQuery(event.target.value)}
                    value={query}
                    variant="outlined"
                    sx={{ ml: "10px", mt: "10px", pr: "20px" }}
                    type="search"
                />
                <Filters
                    itemType={itemType}
                    allowHidingUnsupportedItems={allItemSubtypes?.length > 0}
                    showUnsupportedItems={showUnsupportedItems}
                    setShowUnsupportedItems={setShowUnsupportedItems}
                    allowHidingUsedItems={usedItemKeys?.length > 0}
                    hideUsedItems={hideUsedItems}
                    setHideUsedItems={setHideUsedItems}
                    hideUsedItemsScope={hideUsedItemsScope}
                    setHideUsedItemsScope={setHideUsedItemsScope}
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
    usedItemSubtypeKeysInReport: arrayOf(string),
    usedItemSubtypeKeysInSubject: arrayOf(string),
}
