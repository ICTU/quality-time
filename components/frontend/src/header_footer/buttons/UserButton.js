import { Button, Menu, MenuItem } from "@mui/material"
import { func, string } from "prop-types"
import { useState } from "react"

import { logout } from "../../api/auth"
import { Avatar } from "../../widgets/Avatar"

export function UserButton({ user, email, setUser }) {
    const [anchorEl, setAnchorEl] = useState()
    const handleMenu = (event) => setAnchorEl(event.currentTarget)
    const onClickLogout = () => {
        setAnchorEl(null)
        logout()
        setUser(null)
    }
    return (
        <span /* Not using a React fragment (<>) here because that makes the button top-aligned instead of centered */>
            <Button
                aria-label="User options"
                aria-controls="user-options-menu"
                color="inherit"
                onClick={handleMenu}
                startIcon={<Avatar email={email} />}
                sx={{ height: "100%" }}
            >
                {user}
            </Button>
            <Menu id="user-options-menu" anchorEl={anchorEl} onClose={() => setAnchorEl(null)} open={Boolean(anchorEl)}>
                <MenuItem onClick={onClickLogout}>Logout</MenuItem>
            </Menu>
        </span>
    )
}
UserButton.propTypes = {
    user: string,
    email: string,
    setUser: func,
}
