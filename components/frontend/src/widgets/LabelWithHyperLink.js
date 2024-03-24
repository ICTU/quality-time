import { string } from "prop-types"
import { Icon } from "../semantic_ui_react_wrappers"
import { HyperLink } from "./HyperLink"
import { labelPropType } from "../sharedPropTypes"

export function LabelWithHyperLink({ labelId, label, url }) {
    return (
        <label id={labelId}>
            {label}{" "}
            <HyperLink url={url}>
                <Icon name="help circle" link tabIndex="0" />
            </HyperLink>
        </label>
    )
}
LabelWithHyperLink.propTypes = {
    labelId: string,
    label: labelPropType,
    url: string,
}
