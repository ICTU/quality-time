import Brightness4Icon from "@mui/icons-material/Brightness4"
import { IconButton, Menu, MenuItem, Tooltip } from "@mui/material"
import { func } from "prop-types"
import { useState } from "react"

import { uiModePropType } from "../sharedPropTypes"

export function UIModeMenu({ setUIMode, uiMode }) {
    const [anchorEl, setAnchorEl] = useState()
    const handleMenu = (event) => setAnchorEl(event.currentTarget)
    const onClick = (mode) => {
        setAnchorEl(null)
        setUIMode(mode)
    }
    return (
        <Tooltip placement="left" title="Change dark/light mode">
            <span /* https://mui.com/material-ui/react-tooltip/#disabled-elements */>
                <IconButton
                    aria-label="Dark/light mode"
                    aria-controls="dark-light-menu"
                    aria-haspopup="true"
                    color="inherit"
                    onClick={handleMenu}
                    size="large"
                    sx={{ height: "100%" }}
                >
                    <Brightness4Icon />
                </IconButton>
                <Menu
                    id="dark-light-menu"
                    anchorEl={anchorEl}
                    onClose={() => setAnchorEl(null)}
                    open={Boolean(anchorEl)}
                >
                    <MenuItem onClick={() => onClick("system")} selected={uiMode === "system"}>
                        Follow OS setting
                    </MenuItem>
                    <MenuItem onClick={() => onClick("dark")} selected={uiMode === "dark"}>
                        Dark mode
                    </MenuItem>
                    <MenuItem onClick={() => onClick("light")} selected={uiMode === "light"}>
                        Light mode
                    </MenuItem>
                </Menu>
            </span>
        </Tooltip>
    )
}
UIModeMenu.propTypes = {
    setUIMode: func,
    uiMode: uiModePropType,
}
