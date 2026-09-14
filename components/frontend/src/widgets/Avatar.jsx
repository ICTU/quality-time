import { Avatar as MuiAvatar } from "@mui/material"
import { string } from "prop-types"

import { useGravatarUrl } from "../hooks/gravatar"

export function Avatar({ email }) {
    const gravatarUrl = useGravatarUrl(email ?? "")
    return <MuiAvatar alt={`Avatar for ${email}`} src={gravatarUrl} sx={{ width: 24, height: 24 }} />
}
Avatar.propTypes = {
    email: string,
}
