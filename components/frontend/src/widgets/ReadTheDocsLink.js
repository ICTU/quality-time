import HelpIcon from "@mui/icons-material/Help"
import { string } from "prop-types"

import { HyperLink } from "./HyperLink"

export function ReadTheDocsLink({ url }) {
    return (
        <HyperLink url={url}>
            Read the Docs <HelpIcon fontSize="small" sx={{ verticalAlign: "middle" }} />
        </HyperLink>
    )
}
ReadTheDocsLink.propTypes = {
    url: string,
}
