import { Chip } from "@mui/material"
import { string } from "prop-types"

import { Header } from "../semantic_ui_react_wrappers"
import { sourceTypePropType } from "../sharedPropTypes"
import { slugify } from "../utils"
import { ReadTheDocsLink } from "../widgets/ReadTheDocsLink"
import { Logo } from "./Logo"
import { sourceTypeDescription } from "./SourceType"

export function SourceTypeHeader({ metricTypeId, sourceTypeId, sourceType }) {
    let howToConfigure = ""
    if (sourceType?.documentation?.generic || sourceType?.documentation?.[metricTypeId]) {
        howToConfigure = " for specific information on how to configure this source type."
    }
    const url = `https://quality-time.readthedocs.io/en/v${process.env.REACT_APP_VERSION}/reference.html${slugify(sourceType.name)}`
    return (
        <Header>
            <Header.Content>
                <Logo logo={sourceTypeId} alt={sourceType.name} />
                {sourceType.name}
                {sourceType.deprecated && <Chip color="warning" label="Deprecated" sx={{ marginLeft: "8px" }} />}
                <Header.Subheader>
                    {`${sourceTypeDescription(sourceType)} `}
                    <ReadTheDocsLink url={url} />
                    {howToConfigure}
                </Header.Subheader>
            </Header.Content>
        </Header>
    )
}
SourceTypeHeader.propTypes = {
    metricTypeId: string,
    sourceTypeId: string,
    sourceType: sourceTypePropType,
}
