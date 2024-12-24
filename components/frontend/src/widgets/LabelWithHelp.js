import HelpIcon from "@mui/icons-material/Help"
import { Tooltip } from "@mui/material"
import { string } from "prop-types"

import { labelPropType, popupContentPropType } from "../sharedPropTypes"

export function LabelWithHelp({ labelId, labelFor, label, help }) {
    return (
        <label id={labelId} htmlFor={labelFor}>
            {label}{" "}
            <Tooltip title={help}>
                <HelpIcon fontSize="inherit" tabIndex="0" />
            </Tooltip>
        </label>
    )
}
LabelWithHelp.propTypes = {
    labelId: string,
    labelFor: string,
    label: labelPropType,
    help: popupContentPropType,
}
