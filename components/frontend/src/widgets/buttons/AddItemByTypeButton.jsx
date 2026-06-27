import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown"
import { Button, Tooltip } from "@mui/material"
import { array, arrayOf, bool, func, string } from "prop-types"

import { AddItemIcon } from "../icons"
import { ItemTypeSelector } from "../ItemTypeSelector"

export function AddItemByTypeButton({
    itemSubtypes,
    itemType,
    onClick,
    allItemSubtypes,
    usedItemSubtypeKeysInReport,
    usedItemSubtypeKeysInSubject,
    sort,
}) {
    return (
        <ItemTypeSelector
            allItemSubtypes={allItemSubtypes}
            itemSubtypes={itemSubtypes}
            itemType={itemType}
            onClick={onClick}
            renderAnchor={(handleMenu) => (
                <Tooltip title={`Add a new ${itemType} here`} placement="top">
                    <Button aria-describedby="dropdown-menu" onClick={handleMenu} variant="outlined">
                        <AddItemIcon /> {`Add ${itemType} `} <ArrowDropDownIcon />
                    </Button>
                </Tooltip>
            )}
            sort={sort}
            usedItemSubtypeKeysInReport={usedItemSubtypeKeysInReport}
            usedItemSubtypeKeysInSubject={usedItemSubtypeKeysInSubject}
        />
    )
}
AddItemByTypeButton.propTypes = {
    allItemSubtypes: array,
    itemSubtypes: array,
    itemType: string,
    onClick: func,
    sort: bool,
    usedItemSubtypeKeysInReport: arrayOf(string),
    usedItemSubtypeKeysInSubject: arrayOf(string),
}
