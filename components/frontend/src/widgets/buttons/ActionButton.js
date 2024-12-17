import { Button, Tooltip } from "@mui/material"
import { bool, element, func, string } from "prop-types"

import { popupContentPropType } from "../../sharedPropTypes"

export function ActionButton(props) {
    const { action, color, disabled, icon, itemType, onClick, popup } = props
    const label = `${action} ${itemType}`
    return (
        <Tooltip title={popup}>
            <span /* https://mui.com/material-ui/react-tooltip/#disabled-elements */>
                <Button color={color} disabled={disabled} onClick={() => onClick()} startIcon={icon} variant="outlined">
                    {label}
                </Button>
            </span>
        </Tooltip>
    )
}
ActionButton.propTypes = {
    action: string,
    color: string,
    disabled: bool,
    icon: element,
    itemType: string,
    onClick: func,
    popup: popupContentPropType,
}
