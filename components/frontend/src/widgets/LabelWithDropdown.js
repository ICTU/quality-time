import { array, func, oneOf, string } from "prop-types"

import { Dropdown } from "../semantic_ui_react_wrappers"
import { labelPropType } from "../sharedPropTypes"

export function LabelWithDropdown({ color, direction, label, onChange, options, value }) {
    return (
        <label>
            {label}
            <span style={{ paddingLeft: "6mm", color: color || "black" }}>
                <Dropdown
                    color={color}
                    direction={direction}
                    inline
                    onChange={onChange}
                    options={options}
                    tabIndex="0"
                    value={value}
                />
            </span>
        </label>
    )
}
LabelWithDropdown.propTypes = {
    color: string,
    direction: oneOf(["left", "right"]),
    label: labelPropType,
    onChange: func,
    options: array,
    value: string,
}
