import { Header } from "../semantic_ui_react_wrappers"
import { string } from "prop-types"
import { PermLinkButton } from "../widgets/Button"

export function Share({ title, url }) {
    return (
        <>
            <Header size="small">{title}</Header>
            <PermLinkButton url={url} />
        </>
    )
}
Share.propTypes = {
    title: string,
    url: string,
}
