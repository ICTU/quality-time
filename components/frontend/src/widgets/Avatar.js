import MD5 from "crypto-js/md5"
import { string } from "prop-types"
import { useContext } from "react"
import { Icon, Image } from "semantic-ui-react"

import { DarkMode } from "../context/DarkMode"

export function Avatar({ email }) {
    const color = useContext(DarkMode) ? "grey" : null
    return email ? (
        <Image avatar src={`https://www.gravatar.com/avatar/${MD5(email)}?d=identicon`} alt="Avatar" />
    ) : (
        <Icon color={color} name="user" />
    )
}
Avatar.propTypes = {
    email: string,
}
