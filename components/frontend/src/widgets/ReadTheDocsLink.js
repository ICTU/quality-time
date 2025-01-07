import { string } from "prop-types"

import { HyperLink } from "./HyperLink"

export function ReadTheDocsLink({ url }) {
    return <HyperLink url={url}>Read the Docs</HyperLink>
}
ReadTheDocsLink.propTypes = {
    url: string,
}
