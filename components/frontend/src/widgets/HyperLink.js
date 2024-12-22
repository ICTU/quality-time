import { Link } from "@mui/material"
import { string } from "prop-types"

import { childrenPropType } from "../sharedPropTypes"

export function HyperLink({ url, children }) {
    return (
        <Link
            color="inherit"
            href={url}
            onClick={(event) => event.stopPropagation()}
            rel="noreferrer"
            target="_blank"
            title="Opens new window or tab"
            underline="always"
        >
            {children}
        </Link>
    )
}
HyperLink.propTypes = {
    url: string,
    children: childrenPropType,
}
