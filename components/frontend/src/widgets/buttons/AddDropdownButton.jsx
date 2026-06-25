import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown"
import { Button } from "@mui/material"
import { array, arrayOf, bool, func, string } from "prop-types"

import { AddItemIcon } from "../icons"
import { ItemSelector } from "../ItemSelector"

export function AddDropdownButton({
    itemSubtypes,
    itemType,
    onClick,
    allItemSubtypes,
    usedItemSubtypeKeysInReport,
    usedItemSubtypeKeysInSubject,
    sort,
}) {
    return (
        <ItemSelector
            allItemSubtypes={allItemSubtypes}
            itemSubtypes={itemSubtypes}
            itemType={itemType}
            onClick={onClick}
            renderAnchor={(handleMenu) => (
                <Button aria-describedby="dropdown-menu" onClick={handleMenu} variant="outlined">
                    <AddItemIcon /> {`Add ${itemType} `} <ArrowDropDownIcon />
                </Button>
            )}
            sort={sort}
            tooltip={`Add a new ${itemType} here`}
            usedItemSubtypeKeysInReport={usedItemSubtypeKeysInReport}
            usedItemSubtypeKeysInSubject={usedItemSubtypeKeysInSubject}
        />
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
