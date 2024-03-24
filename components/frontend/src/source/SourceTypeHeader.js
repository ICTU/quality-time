import { string } from "prop-types"
import { Header, Icon } from "../semantic_ui_react_wrappers"
import { HyperLink } from "../widgets/HyperLink"
import { Logo } from "./Logo"
import { slugify } from "../utils"
import { sourceTypePropType } from "../sharedPropTypes"

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
                <Header.Subheader>
                    {sourceType.description}{" "}
                    <HyperLink url={url}>
                        Read the Docs <Icon name="external" link />
                    </HyperLink>
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
