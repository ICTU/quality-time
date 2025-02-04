import { Avatar as MuiAvatar } from "@mui/material"
import MD5 from "crypto-js/md5"
import { string } from "prop-types"

export function Avatar({ email }) {
    return (
        <MuiAvatar
            alt={`Avatar for ${email}`}
            src={`https://www.gravatar.com/avatar/${MD5(email ?? "")}?d=identicon`}
            sx={{ width: 24, height: 24 }}
        />
    )
}
Avatar.propTypes = {
    email: string,
}
