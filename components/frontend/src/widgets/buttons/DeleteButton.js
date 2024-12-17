import { string } from "prop-types"

import { DeleteItemIcon } from "../icons"
import { ActionButton } from "./ActionButton"

export function DeleteButton(props) {
    return (
        <ActionButton
            action="Delete"
            color="warning"
            icon={<DeleteItemIcon />}
            popup={`Delete this ${props.itemType}. Careful, this can only be undone by a system administrator!`}
            {...props}
        />
    )
}
DeleteButton.propTypes = {
    itemType: string,
}
