import { bool, func, number, oneOfType, string } from "prop-types"
import { Menu } from "semantic-ui-react"

import { Popup } from "../semantic_ui_react_wrappers"
import { childrenPropType, popupContentPropType } from "../sharedPropTypes"

const activeColor = "grey"

export function SettingsMenuItem({ active, children, disabled, disabledHelp, help, onClick, onClickData }) {
    // A menu item that can can show help when disabled so users can see why the menu item is disabled
    const props = {
        active: active,
        color: activeColor,
        disabled: disabled,
        onBeforeInput: (event) => {
            event.preventDefault()
            if (!disabled) {
                onClick(onClickData)
            }
        }, // Uncovered, see https://github.com/testing-library/react-testing-library/issues/1152
        onClick: (event) => {
            event.preventDefault()
            onClick(onClickData)
        },
        tabIndex: 0,
    }
    if (help || (disabledHelp && disabled)) {
        props["style"] = { marginLeft: 0, marginRight: 0, marginBottom: 5 } // Compensate for the span
        return (
            <Popup
                content={disabledHelp || help}
                inverted
                position="left center"
                // We need a span here to prevent the popup from becoming disabled when the menu item is disabled:
                trigger={
                    <span>
                        <Menu.Item {...props}>{children}</Menu.Item>
                    </span>
                }
            />
        )
    }
    return <Menu.Item {...props}>{children}</Menu.Item>
}
SettingsMenuItem.propTypes = {
    active: bool,
    children: childrenPropType,
    disabled: bool,
    disabledHelp: popupContentPropType,
    help: popupContentPropType,
    onClick: func,
    onClickData: oneOfType([bool, number, string]),
}
