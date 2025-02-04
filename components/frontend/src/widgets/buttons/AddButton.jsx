import { func, string } from "prop-types"

import { AddItemIcon } from "../icons"
import { ActionButton } from "./ActionButton"

export function AddButton({ itemType, onClick }) {
    return (
        <ActionButton
            action="Add"
            icon={<AddItemIcon />}
            itemType={itemType}
            onClick={onClick}
            popup={`Add a new ${itemType} here`}
        />
    )
}
AddButton.propTypes = {
    itemType: string,
    onClick: func,
}
