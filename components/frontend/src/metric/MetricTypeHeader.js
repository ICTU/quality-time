import { Header } from "../semantic_ui_react_wrappers"
import { metricTypePropType } from "../sharedPropTypes"
import { referenceDocumentationURL } from "../utils"
import { ReadTheDocsLink } from "../widgets/ReadTheDocsLink"

export function MetricTypeHeader({ metricType }) {
    const howToConfigure = metricType.documentation
        ? " for specific information on how to configure this metric type."
        : ""
    return (
        <Header>
            <Header.Content>
                {metricType.name}
                <Header.Subheader>
                    {metricType.description} <ReadTheDocsLink url={referenceDocumentationURL(metricType.name)} />
                    {howToConfigure}
                </Header.Subheader>
            </Header.Content>
        </Header>
    )
}
MetricTypeHeader.propTypes = {
    metricType: metricTypePropType,
}
