import HelpIcon from "@mui/icons-material/Help"
import { bool, string } from "prop-types"

import { Popup } from "../semantic_ui_react_wrappers"
import { labelPropType, popupContentPropType } from "../sharedPropTypes"

export function LabelWithHelp({ labelId, labelFor, label, help, hoverable }) {
    return (
        <label id={labelId} htmlFor={labelFor}>
            {label}{" "}
            <Popup
                hoverable={hoverable}
                on={["hover", "focus"]}
                content={help}
                trigger={<HelpIcon fontSize="inherit" tabIndex="0" />}
                wide
            />
        </label>
    )
}
LabelWithHelp.propTypes = {
    labelId: string,
    labelFor: string,
    label: labelPropType,
    help: popupContentPropType,
    hoverable: bool,
}
