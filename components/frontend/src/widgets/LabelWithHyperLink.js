import HelpIcon from "@mui/icons-material/Help"
import { string } from "prop-types"

import { labelPropType } from "../sharedPropTypes"
import { HyperLink } from "./HyperLink"

export function LabelWithHyperLink({ labelId, label, url }) {
    return (
        <label id={labelId}>
            {label}{" "}
            <HyperLink url={url}>
                <HelpIcon fontSize="inherit" />
            </HyperLink>
        </label>
    )
}
LabelWithHyperLink.propTypes = {
    labelId: string,
    label: labelPropType,
    url: string,
}
