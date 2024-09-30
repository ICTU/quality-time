import { MenuItem, MenuList, Stack, Tooltip, Typography } from "@mui/material"
import { bool, func, number, oneOfType, string } from "prop-types"

import { childrenPropType, popupContentPropType } from "../../sharedPropTypes"

export function SettingsMenuGroup({ children }) {
    return (
        <Stack direction="row" sx={{ justifyContent: "space-between", padding: "20px" }}>
            {children}
        </Stack>
    )
}
SettingsMenuGroup.propTypes = {
    children: childrenPropType,
}

export function SettingsMenu({ children, title }) {
    return (
        <Stack>
            <Typography variant="h6">{title}</Typography>
            <MenuList>{children}</MenuList>
        </Stack>
    )
}
SettingsMenu.propTypes = {
    title: string,
    children: childrenPropType,
}

export function SettingsMenuItem({ active, children, disabled, disabledHelp, help, onClick, onClickData }) {
    // A menu item that can can show help when disabled so users can see why the menu item is disabled
    const props = {
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
        selected: active,
        tabIndex: 0,
    }
    if (help || (disabledHelp && disabled)) {
        return (
            <Tooltip placement="left" title={disabledHelp || help}>
                <span /* https://mui.com/material-ui/react-tooltip/#disabled-elements */>
                    <MenuItem {...props}>{children}</MenuItem>
                </span>
            </Tooltip>
        )
    }
    return <MenuItem {...props}>{children}</MenuItem>
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
