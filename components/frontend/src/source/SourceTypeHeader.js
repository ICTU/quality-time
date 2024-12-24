import { Chip } from "@mui/material"
import { string } from "prop-types"

import { sourceTypePropType } from "../sharedPropTypes"
import { slugify } from "../utils"
import { Header } from "../widgets/Header"
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
        <Header
            header={
                <>
                    <Logo logo={sourceTypeId} alt={sourceType.name} /> {sourceType.name}
                    {sourceType.deprecated && <Chip color="warning" label="Deprecated" sx={{ marginLeft: "8px" }} />}
                </>
            }
            level="h4"
            subheader={
                <>
                    {`${sourceTypeDescription(sourceType)} `}
                    <ReadTheDocsLink url={url} />
                    {howToConfigure}
                </>
            }
        />
    )
}
SourceTypeHeader.propTypes = {
    metricTypeId: string,
    sourceTypeId: string,
    sourceType: sourceTypePropType,
}
