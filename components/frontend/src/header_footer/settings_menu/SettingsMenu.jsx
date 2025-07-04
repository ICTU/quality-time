import { MenuItem, MenuList, Stack, Tooltip, Typography } from "@mui/material"
import { bool, func, number, oneOf, oneOfType, string } from "prop-types"

import { childrenPropType, popupContentPropType } from "../../sharedPropTypes"

export function SettingsMenuGroup({ children, justify }) {
    return (
        <Stack direction="row" spacing={5} sx={{ justifyContent: justify ?? "left", padding: "16px" }}>
            {children}
        </Stack>
    )
}
SettingsMenuGroup.propTypes = {
    children: childrenPropType,
    justify: oneOf(["left", "right"]),
}

export function SettingsMenu({ children, title }) {
    return (
        <Stack>
            <Typography variant="h3" noWrap>
                {title}
            </Typography>
            <MenuList dense disablePadding>
                {children}
            </MenuList>
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
                <span role="menu" /* https://mui.com/material-ui/react-tooltip/#disabled-elements */>
                    <MenuItem {...props} disableGutters sx={{ paddingLeft: "2px", paddingRight: "2px" }}>
                        {children}
                    </MenuItem>
                </span>
            </Tooltip>
        )
    }
    return (
        <MenuItem {...props} disableGutters sx={{ paddingLeft: "2px", paddingRight: "2px" }}>
            {children}
        </MenuItem>
    )
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
